from fastapi import FastAPI
from models import FinancialAccount, Income, Expense

app = FastAPI()


fin_acc = FinancialAccount(balance=0.0)
incomes = fin_acc.incomes
expenses = fin_acc.expenses


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/incomes")
async def get_incomes():
    return {"incomes": incomes}


@app.post("/incomes")
def create_income(income: Income):
    incomes.append(income)
    return {"message": f"Income {income.name} has been added"}


@app.get("/expenses")
async def get_expenses():
    return {"expenses": expenses}


@app.post("/expenses")
def create_income(expense: Expense):
    expenses.append(expense)
    return {"message": f"Expense {expense.name} has been added"}


@app.get("/balance")
async def get_balance():

    balance = fin_acc.get_balance(expenses, incomes)

    return {"balance": balance}
