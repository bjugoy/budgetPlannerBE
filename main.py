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
from database_models.financials import Income, Expenses

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

fin_acc = FinancialAccount(balance=0.0)


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


# ----- SESSION MANAGEMENT -----

class Session(BaseModel):
    session_id: int
    username: str


users = []
sessions = []
next_session_id = 1


@app.get("/users", response_model=List[User])
async def read_users():
    return users


@app.get("/sessions", response_model=List[Session])
async def read_sessions():
    return sessions


@app.post("/login")
async def login(authentication: Authentication):
    global next_session_id

    stored_user = next((u for u in users if u.username == authentication.username), None)

    if not stored_user or not bcrypt.checkpw(authentication.password.encode('utf-8'),
                                             stored_user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    existing_session = next((s for s in sessions if s.username == stored_user.username), None)

    if existing_session:
        response = {"message": "Login successful"}
    else:
        new_session_id = next_session_id
        next_session_id += 1

        new_session = Session(session_id=new_session_id, username=stored_user.username)
        sessions.append(new_session)

        response = {"message": "Login successful"}

        response_headers = {"Set-Cookie": f"session_id={new_session_id}; HttpOnly"}
        return JSONResponse(content=response, headers=response_headers)

    return response


@app.post("/register")
async def register(user: User):
    # Check if username is already taken
    if any(u.username == user.username for u in users):
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hashed_password,
        accounts=[]
    )

    users.append(new_user)

    response = {"message": "Registration successful"}
    return response


@app.post("/logout")
async def logout(session_id: int = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session_index = next((i for i, s in enumerate(sessions) if s.session_id == session_id), None)

    if session_index is not None:
        sessions.pop(session_index)

    response = {"message": "Logged out successfully"}
    return response
