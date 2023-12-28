
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import event, Engine
from sqlalchemy.orm import Session
from database import session, engine
from typing import Annotated
from database_models import base
import models

# man muss unterscheiden unter Income von BE und DB
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


# database session
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
                       category=income.category)
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


@app.get("/expenses")
async def read_expenses(db: db_dependency, skip: int = 0, limit: int = 100):
    expenses = db.query(Expenses).offset(skip).limit(limit).all()
    return {"expenses": expenses}


@app.post("/expenses", response_model=ExpenseModel)
async def create_expense(expense: ExpenseBase, db: db_dependency):
    db_expense = Expenses(name=expense.name,
                          amount=expense.amount,
                          description=expense.description,
                          isMonthly=expense.isMonthly,
                          category=expense)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"message": f"Expense {expense.name} has been added"}


@app.get("/balance")
async def get_balance(db: db_dependency):
    incomes = db.query(Income).all()
    expenses = db.query(Expenses).all()

    balance = fin_acc.get_balance(expenses, incomes)
    return {"balance": balance}
