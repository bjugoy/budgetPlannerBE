import os.path

from fastapi import FastAPI
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker

#man muss unterscheiden unter Income von BE und DB
from models import FinancialAccount, Income as APIIncome, Expense as APIExpense
from database_models.financials import Income as DBIncome, Expenses as DBExpense
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

#gebe damit nur den Pfad von diesem File an, den absoluten Pfad -J
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#engine ist verantwortlich für Interaktion mit Datenbank(SQLite) -J
engine = create_engine(f"sqlite:///{BASE_DIR}/db", echo=True)

#sorgt dafür, dass immer die selbe session verwendet wird und nicht immer eine neue Verbindung aufgebaut werden muss -J
session = scoped_session(
    sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine,
    )
)


#das ich Fremdschlüssel verwendet kann (ForeignKeys) -J
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection,connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

fin_acc = FinancialAccount(balance=0.0)
incomes = fin_acc.incomes
expenses = fin_acc.expenses

#avoid cors error
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
async def get_incomes():
    return {"incomes": incomes}


@app.post("/incomes")
async def create_income(income: APIIncome):
    db_income = DBIncome(source_of_income=income.name, amount_of_income=income.amount, description=income.comment)
    session.add(db_income)
    session.commit()
    #fin_acc.incomes.append(income)
    return {"message": f"Income {income.name} has been added"}


@app.get("/expenses")
async def get_expenses():
    return {"expenses": expenses}


@app.post("/expenses")
async def create_expense(expense: APIExpense):
    fin_acc.expenses.append(expense)
    return {"message": f"Expense {expense.name} has been added"}


@app.get("/balance")
async def get_balance():
    total_income = sum(income.amount for income in fin_acc.incomes)
    total_expense = sum(expense.amount for expense in fin_acc.expenses)
    current_balance = total_income - total_expense
    return {"balance": current_balance}
