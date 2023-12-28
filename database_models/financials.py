from sqlalchemy import Column, Integer, String, Float, Boolean

from database_models.base import TimeStampedModel


class Income(TimeStampedModel):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    amount = Column(Float)
    description = Column(String(200))
    isMonthly = Column(Boolean, default=True)
    category = Column(String)


class Expenses(TimeStampedModel):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    amount = Column(Float)
    description = Column(String(200))
    isMonthly = Column(Boolean, default=True)
    category = Column(String)


