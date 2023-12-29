from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


class Entry(BaseModel):
    name: str
    amount: float
    description: Optional[str] = None


class IncomeCategory(Enum):
    SALARY = "Salary"
    INVESTMENT_DIVIDENDS = "Investment Dividends"
    CAPITAL_GAIN = "Capital Gain"
    ADDITIONAL_INCOME = "Additional Income"


class ExpenseCategory(Enum):
    FOOD = "Food"
    BILLS = "Bills"
    SUBSCRIPTIONS = "Subscriptions"
    GROCERIES = "Groceries"
    MEDICINE = "Medicine"
    INVESTMENTS = "Investments"
    CLOTHING = "Clothing"
    RENT = "Rent"
    INSURANCE = "Insurance"
    CAR = "Car"


class IncomeBase(Entry):
    isMonthly: bool
    category: Optional[IncomeCategory] = None


class IncomeModel(IncomeBase):
    id: int

    class Config:
        orm_mode = True


class ExpenseBase(Entry):
    isMonthly: bool
    category: Optional[ExpenseCategory] = None


class ExpenseModel(ExpenseBase):
    id: int

    class Config:
        orm_mode = True


class FinancialAccount(BaseModel):
    balance: float
    expenses: List[ExpenseBase] = []
    incomes: List[IncomeBase] = []

    @staticmethod
    def get_balance(expenses, incomes):

        total_expenses = sum(expense.amount for expense in expenses)
        total_incomes = sum(income.amount for income in incomes)

        return total_incomes - total_expenses


class User(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    accounts: List[str] = []


class Authentication(BaseModel):
    username: str
    password: str
