from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey

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


class Expenses(TimeStampedModel):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    amount = Column(Float)
    description = Column(String(200))
    isMonthly = Column(Boolean, default=True)
    category = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer)

