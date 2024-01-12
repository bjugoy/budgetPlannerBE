from fastapi import FastAPI, HTTPException, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from sqlalchemy import event, Engine
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from database import session, engine
from typing import Annotated
from database_models import base

from models import *
from database_models.financials import Income, Expenses, User, FinancialAccount

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# das ich Fremdschlüssel verwendet kann (ForeignKeys) -J
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# gibt eine database session zurück
def get_db():
    db = session
    try:
        yield db
    finally:
        db.close()


# db_dependency ist vom Typ Session
# ruft get_db auf
db_dependency = Annotated[Session, Depends(get_db)]


# erstellt tabellen
base.Base.metadata.create_all(bind=engine)

fin_acc = FinancialAccountBase(balance=0.0)


# avoid cors error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/incomes")
async def read_incomes(db: db_dependency, skip: int = 0, limit: int = 100):
    incomes = db.query(Income).offset(skip).limit(limit).all()
    return {"incomes": incomes}


@app.post("/incomes", response_model=IncomeModel)
async def create_income(income: IncomeBase, db: db_dependency):
    db_income = Income(name=income.name,
                       amount=income.amount,
                       description=income.description,
                       isMonthly=income.isMonthly,
                       category=income.category.value)
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


@app.get("/expenses")
# skip = 0 --> keine Reihe wird übersprungen bei offset()
async def read_expenses(db: db_dependency, skip: int = 0, limit: int = 100):
    expenses = db.query(Expenses).offset(skip).limit(limit).all()
    return {"expenses": expenses}


@app.post("/expenses", response_model=ExpenseModel)
async def create_expense(expense: ExpenseBase, db: db_dependency):
    db_expense = Expenses(name=expense.name,
                          amount=expense.amount,
                          description=expense.description,
                          isMonthly=expense.isMonthly,
                          category=expense.category.value)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.get("/balance")
async def get_balance(db: db_dependency):
    incomes = [income.amount for income in db.query(Income).all()]
    expenses = [expense.amount for expense in db.query(Expenses).all()]

    total_income = sum(incomes)
    total_expense = sum(expenses)

    balance = total_income - total_expense
    return {"balance": balance}


@app.post("/users/{user_id}/financial-accounts", response_model=FinancialAccountModel)
async def add_financial_account_to_user(
    user_id: int,
    financial_account: FinancialAccountBase,
    db: Session = Depends(get_db)
):
    try:
        # Check if the user exists
        existing_user = db.query(UserBase).filter(UserBase.id == user_id).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create the financial account and associate it with the user
        db_financial_account = FinancialAccount(user_id=existing_user.id,
                                                balance=financial_account.balance)
        db.add(db_financial_account)
        db.commit()
        db.refresh(db_financial_account)

        return {"status": "success", "message": "Financial account added successfully", "data": db_financial_account}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}


# ----- SESSION MANAGEMENT -----

class Session(BaseModel):
    session_id: int
    user_id: str


sessions = []
next_session_id = 1


@app.get("/users", response_model=List[UserBase])
async def read_users(db: Session = Depends(get_db)):
    users = db.query(UserBase).all()
    return users


@app.get("/sessions", response_model=List[Session])
async def read_sessions():
    return sessions


@app.post("/login")
async def login(authentication: Authentication, db: Session = Depends(get_db)):
    global next_session_id

    stored_user = db.query(UserBase).filter(UserBase.username == authentication.username).first()

    if not stored_user or not bcrypt.checkpw(authentication.password.encode('utf-8'),
                                             stored_user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    existing_session = next((s for s in sessions if s.user_id == stored_user.id), None)

    if existing_session:
        response = {"message": "Login successful"}
    else:
        new_session_id = next_session_id
        next_session_id += 1

        new_session = Session(session_id=new_session_id, user_id=stored_user.id)
        sessions.append(new_session)

        response = {"message": "Login successful"}

        response_headers = {"Set-Cookie": f"session_id={new_session_id}; HttpOnly"}
        return JSONResponse(content=response, headers=response_headers)

    return response


@app.post("/register", response_model=UserModel)
async def register(user: UserBase, db: Session = Depends(get_db)):
    # Check if username is already taken
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()

    return new_user


@app.post("/logout")
async def logout(session_id: int = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session_index = next((i for i, s in enumerate(sessions) if s.session_id == session_id), None)

    if session_index is not None:
        sessions.pop(session_index)

    response = {"message": "Logged out successfully"}
    return response


def get_current_active_user(session_id: int = Cookie(None), db: Session = Depends(get_db)):
    active_session = next((s for s in sessions if s.session_id == session_id), None)
    if not active_session:
        raise HTTPException(status_code=401, detail="Not logged in")

    active_user = db.query(UserBase).filter(UserBase.id == active_session.user_id).first()
    if not active_user:
        raise HTTPException(status_code=401, detail="User not found")

    return active_user
