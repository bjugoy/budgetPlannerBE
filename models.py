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


# ___Model for Database and response model of endpoint
class ExpenseModel(ExpenseBase):
    id: int

    class Config:
        orm_mode = True


class FinancialAccountBase(BaseModel):
    balance: float
    expenses: List[ExpenseBase] = []
    incomes: List[IncomeBase] = []


class FinancialAccountModel(FinancialAccountBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str


class UserModel(UserBase):
    id: int

    class Config:
        orm_mode = True


class Authentication(BaseModel):
    username: str
    password: str
