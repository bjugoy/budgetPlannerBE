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
    user_id = Column(Integer, ForeignKey("users.id"))  # Foreign key to link income with user

    user = relationship("User", back_populates="incomes")


class Expenses(TimeStampedModel):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    amount = Column(Float)
    description = Column(String(200))
    isMonthly = Column(Boolean, default=True)
    category = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))  # Foreign key to link expense with user

    user = relationship("User", back_populates="expenses")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)

    incomes = relationship("Income", back_populates="user")
    expenses = relationship("Expenses", back_populates="user")
    sessions = relationship("DBSession", back_populates="user")


class DBSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="sessions")
