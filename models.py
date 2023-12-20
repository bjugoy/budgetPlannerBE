from pydantic import BaseModel
from typing import List


class Entry(BaseModel):
    id: int
    amount: float
    name: str
    comment: str


class Income(Entry):
    isMonthly: bool


class Expense(Entry):
    isMonthly: bool


class FinancialAccount(BaseModel):
    balance: float
    expenses: List[Expense] = []
    incomes: List[Income] = []

    @staticmethod
    def get_balance(expenses, incomes):

        total_expenses = sum(expense.amount for expense in expenses)
        total_incomes = sum(income.amount for income in incomes)

        return total_incomes - total_expenses
