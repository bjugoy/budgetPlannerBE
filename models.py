from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
import datetime


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
    date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True


class IncomeModel(IncomeBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class ExpenseBase(Entry):
    isMonthly: bool
    category: Optional[ExpenseCategory] = None
    date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True


class ExpenseModel(ExpenseBase):
    id: int
    user_id: int

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


class SessionBase(BaseModel):
    session_id: int


class SessionModel(SessionBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
