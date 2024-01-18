from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Depends, Cookie, Response, Request
import bcrypt
from sqlalchemy import event, Engine
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from database import session, engine
from typing import Annotated, Type, Union
from database_models import base

from models import *
from database_models.financials import Income, Expenses, User, DBSession

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


# avoid cors error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    print("Received Session ID:", session_id)  #for debugging
    if session_id:
        db_session = db.query(DBSession).filter_by(session_id=session_id).first()

        if db_session:
            user_id = db_session.user_id
            user = db.query(User).filter_by(id=user_id).first()

            if user:
                return user

    return None


def get_financial_records( # alle parameter
    db: db_dependency,
    model: Type[Union[Income, Expenses]],
    current_user: User,
    is_monthly: Optional[bool] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # zuerst nach user filtern, dann optional (if) nach is_monthly
    query = db.query(model).filter_by(user_id=current_user.id)
    if is_monthly is not None:
        query = query.filter_by(isMonthly=is_monthly)

    if category:
        query = query.filter_by(category=category)

    # Apply offset and limit
    records = query.offset(skip).limit(limit).all()
    return records or []


"""                             ----- GET ENDPOINTS -----                                  """


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/incomes", response_model=List[IncomeModel])
async def read_incomes(
    db: db_dependency,
    current_user: User = Depends(get_current_user),
    is_monthly: Optional[bool] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    return get_financial_records(db, Income, current_user, is_monthly, category, skip, limit)


@app.get("/expenses", response_model=List[ExpenseModel])
async def read_expenses(
    db: db_dependency,
    current_user: User = Depends(get_current_user),
    is_monthly: Optional[bool] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    return get_financial_records(db, Expenses, current_user, is_monthly, category, skip, limit)


@app.get("/balance")
async def get_balance(db: db_dependency, current_user: User = Depends(get_current_user)):
    print("Current User:", current_user)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Retrieve incomes and expenses associated with the current user
    incomes = db.query(Income).filter_by(user_id=current_user.id).all()
    expenses = db.query(Expenses).filter_by(user_id=current_user.id).all()

    # Calculate the total income and total expense
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)

    # Calculate the balance
    balance = total_income - total_expense

    return {"balance": balance}


@app.get("/income-categories")
def get_income_categories():
    return [category.value for category in IncomeCategory]


@app.get("/expense-categories")
def get_income_categories():
    return [category.value for category in ExpenseCategory]


@app.get("/current_user")
async def get_current_user_route(current_user: User = Depends(get_current_user)):
    if current_user:
        return {"username": current_user.username}
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


""""                                 ----- POST ENDPOINTS -----                               """


@app.post("/incomes", response_model=IncomeModel)
async def create_income(income: IncomeBase, db: db_dependency, current_user: User = Depends(get_current_user)):
    db_income = Income(
        name=income.name,
        amount=income.amount,
        description=income.description,
        isMonthly=income.isMonthly,
        category=income.category.value,
        user_id=current_user.id # Set the user associated with the income
    )
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


@app.post("/expenses", response_model=ExpenseModel)
async def create_expense(expense: ExpenseBase, db: db_dependency, current_user: User = Depends(get_current_user)):
    db_expense = Expenses(
        name=expense.name,
        amount=expense.amount,
        description=expense.description,
        isMonthly=expense.isMonthly,
        category=expense.category.value,
        user_id=current_user.id  # Set the user associated with the expense
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

"""                                 DELETE ENDPOINTS                                   """


@app.delete("/incomes/{income_id}")
async def delete_income(income_id: int, db: db_dependency, current_user: User = Depends(get_current_user)):
    income = db.query(Income).filter_by(id=income_id, user_id=current_user.id).first()
    if income:
        db.delete(income)
        db.commit()
        return {"message": "Income deleted successfully"}
    raise HTTPException(status_code=404, detail="Income not found")


@app.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: int, db: db_dependency, current_user: User = Depends(get_current_user)):
    expense = db.query(Expenses).filter_by(id=expense_id, user_id=current_user.id).first()
    if expense:
        db.delete(expense)
        db.commit()
        return {"message": "Expense deleted successfully"}
    raise HTTPException(status_code=404, detail="Expense not found")


"""                                 ----- SESSION MANAGEMENT -----                               """
next_session_id = 1


@app.get("/users", response_model=List[UserModel])
async def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.get("/sessions", response_model=List[SessionModel])
async def read_sessions(db: Session = Depends(get_db)):
    sessions = db.query(Session).all()
    return sessions


@app.post("/login")
async def login(response: Response, authentication: Authentication, db: db_dependency):
    global next_session_id
    stored_user = db.query(User).filter_by(username=authentication.username).first()

    if not stored_user:
        raise HTTPException(status_code=401, detail="Username not found")

    plaintext_password = str(authentication.password).encode('utf-8')
    hashed_password = str(stored_user.password).encode('utf-8')

    if not bcrypt.checkpw(plaintext_password,
                          hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    existing_session = db.query(DBSession).filter_by(user_id=stored_user.id).first()

    if existing_session:
        # Set the cookie in the response
        response.set_cookie(key="session_id",
                            value=str(existing_session.session_id),
                            httponly=True,
                            secure=True,
                            samesite='none')
        return {"message": "Login successful"}
    else:
        new_session_id = next_session_id + 1000
        next_session_id += 1

        new_session = DBSession(session_id=new_session_id, user_id=stored_user.id)
        db.add(new_session)
        db.commit()

        # Set the cookie in the response
        response.set_cookie(key="session_id",
                            value=str(new_session_id),
                            httponly=True,
                            secure=True,
                            samesite='none')

        return {"message": "Login successful"}


@app.post("/register", response_model=UserModel)
async def register(user: UserBase, db: Session = Depends(get_db)):
    # Check if username is already taken
    existing_user = db.query(User).filter_by(username=user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hashed_password.decode('utf-8')
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/logout")
async def logout(response: Response, db: db_dependency, session_id: int = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Query the database to find the session by session_id
    db_session = db.query(DBSession).filter_by(session_id=session_id).first()

    if db_session:
        db.delete(db_session)
        db.commit()

        response.delete_cookie("session_id",
                               httponly=True,
                               secure=True,
                               samesite='none')

        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid session ID")
