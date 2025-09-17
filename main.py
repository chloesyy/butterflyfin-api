from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uvicorn

from src import models
from src.database import SessionLocal, engine
from src.utils.logger import logger

app = FastAPI()
# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"

class AccountAddRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the account")
    bank_id: int = Field(..., description="Bank associated with the account")
    account_type: Literal["Savings", "Credit Card", "Investment"] = Field(
        ...,
        description="Type of the account (e.g., savings, checking)"
    )
    initial_balance: float = Field(..., description="Initial balance of the account")

class BankAddRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the bank")
    country: str = Field(..., description="Country where the bank is located")

class CategoryAddRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the category")
    budget: float = Field(0, description="Budget for the category")
    balance: float = Field(0, description="Current balance of the category")

class TransactionAddRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the transaction")
    amount: float = Field(..., description="Transaction amount")
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    category_id: int = Field(..., description="Transaction category ID")
    account_id: int = Field(..., description="Account ID associated with the transaction")


@app.post("/categories/add", response_model=CategoryAddRequest)
def add_category(request: CategoryAddRequest, db: db_dependency):
    db_category = models.Categories(
        name=request.name, 
        budget=request.budget, 
        balance=request.balance
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.post("/categories/{category_id}/delete")
def delete_category(category_id: int, db: db_dependency):
    db_category = db.query(models.Categories).filter(models.Categories.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"detail": "Category deleted"}

@app.post("/accounts/add", response_model=AccountAddRequest)
def add_account(request: AccountAddRequest, db: db_dependency):
    db_account = models.Accounts(
        name=request.name,
        bank_id=request.bank_id,
        account_type=request.account_type,
        initial_balance=request.initial_balance,
        balance=request.initial_balance
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@app.post("/accounts/{account_id}/delete")
def delete_account(account_id: int, db: db_dependency):
    db_account = db.query(models.Accounts).filter(models.Accounts.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(db_account)
    db.commit()
    return {"detail": "Account deleted"}

@app.post("/banks/add", response_model=BankAddRequest)
def add_bank(request: BankAddRequest, db: db_dependency):
    db_bank = models.Banks(
        name=request.name,
        country=request.country,
        balance=0
    )
    db.add(db_bank)
    db.commit()
    db.refresh(db_bank)
    return db_bank

@app.post("/banks/{bank_id}/delete")
def delete_bank(bank_id: int, db: db_dependency):
    db_bank = db.query(models.Banks).filter(models.Banks.id == bank_id).first()
    if not db_bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    db.delete(db_bank)
    db.commit()
    return {"detail": "Bank deleted"}

@app.post("/transactions/add", response_model=TransactionAddRequest)
def add_transaction(request: TransactionAddRequest, db: db_dependency):
    db_transaction = models.Transactions(
        name=request.name,
        amount=request.amount,
        date=request.date,
        category_id=request.category_id,
        account_id=request.account_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.post("/transactions/{transaction_id}/delete")
def delete_transaction(transaction_id: int, db: db_dependency):
    db_transaction = db.query(models.Transactions).filter(models.Transactions.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(db_transaction)
    db.commit()
    return {"detail": "Transaction deleted"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    logger.info("Server is running at http://localhost:8000")
