from sqlalchemy import Column, Integer, String, Float

from database_models.base import TimeStampedModel


class Income(TimeStampedModel):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_of_income = Column(String(80))
    amount_of_income = Column(Float)

class Expenses(TimeStampedModel):
    __tablename__ = "expenses"

    id= Column(Integer, primary_key=True, autoincrement=True)
    source_of_expenses = Column(String(80))
    amount_of_expense = Column(Float)


