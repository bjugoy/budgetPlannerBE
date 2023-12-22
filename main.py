from fastapi import FastAPI
from models import FinancialAccount, Income, Expense
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


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
async def create_income(income: Income):
    fin_acc.incomes.append(income)
    return {"message": f"Income {income.name} has been added"}


@app.get("/expenses")
async def get_expenses():
    return {"expenses": expenses}


@app.post("/expenses")
async def create_expense(expense: Expense):
    fin_acc.expenses.append(expense)
    return {"message": f"Expense {expense.name} has been added"}


@app.get("/balance")
async def get_balance():
    total_income = sum(income.amount for income in fin_acc.incomes)
    total_expense = sum(expense.amount for expense in fin_acc.expenses)
    current_balance = total_income - total_expense
    return {"balance": current_balance}
