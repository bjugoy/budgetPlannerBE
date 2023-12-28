from pydantic import BaseModel
from typing import List, Optional


class Entry(BaseModel):
    name: str
    amount: float
    description: Optional[str] = None


class IncomeBase(Entry):
    isMonthly: bool
    category: Optional[str] = None


class IncomeModel(IncomeBase):
    id: int

    class Config:
        orm_mode = True


class ExpenseBase(Entry):
    isMonthly: bool
    category: Optional[str] = None


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
