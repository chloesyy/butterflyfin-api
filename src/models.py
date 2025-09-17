"""Database models using SQLAlchemy ORM."""
from sqlalchemy import Column, ForeignKey, Integer, Float, String, UniqueConstraint
from src.database import Base

class Categories(Base):
    """
    Categories model representing the categories table in the database.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    budget = Column(Float, default=0)
    balance = Column(Float, default=0)

class Transactions(Base):
    """
    Transactions model representing the transactions table in the database.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    amount = Column(Float)
    date = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))

class Accounts(Base):
    """
    Accounts model representing the accounts table in the database.
    """
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint('name', 'bank_id', name='uix_name_bank_id'),
        {"sqlite_autoincrement": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bank_id = Column(Integer, ForeignKey("banks.id"))
    account_type = Column(String)
    initial_balance = Column(Float, default=0)
    balance = Column(Float, default=initial_balance)

class Banks(Base):
    """
    Banks model representing the banks table in the database.
    """
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    country = Column(String)
    balance = Column(Float, default=0)
