from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database_models.base import TimeStampedModel
from database import Base


class Income(TimeStampedModel):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    amount = Column(Float)
    description = Column(String(200))
    isMonthly = Column(Boolean, default=True)
    category = Column(String)
    financial_account_id = Column(Integer, ForeignKey('financial_accounts.id'), nullable=False)

    financial_account = relationship("FinancialAccount", back_populates="incomes")


class Expenses(TimeStampedModel):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    amount = Column(Float)
    description = Column(String(200))
    isMonthly = Column(Boolean, default=True)
    category = Column(String)
    financial_account_id = Column(Integer, ForeignKey('financial_accounts.id'), nullable=False)

    financial_account = relationship("FinancialAccount", back_populates="expenses")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)

    financial_accounts = relationship("FinancialAccount", back_populates="user")


class FinancialAccount(TimeStampedModel):
    __tablename__ = "financial_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    balance = Column(Float, default=0.0)

    incomes = relationship("Income", back_populates="financial_account")
    expenses = relationship("Expenses", back_populates="financial_account")
    user = relationship("User", back_populates="financial_accounts")

    @property
    def calc_balance(self):
        total_income = sum(income.amount for income in self.incomes)
        total_expense = sum(expense.amount for expense in self.expenses)
        return total_income - total_expense
