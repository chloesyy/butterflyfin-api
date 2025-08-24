import logging
from colorlog import ColoredFormatter
from typing import Dict, Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.banks import add_bank
from src.accounts import add_account
from src.categories import add_category
from src.transactions import add_transaction
from src.utils.db_utils import delete
from src.utils.logger import logger

app = FastAPI()


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class BankRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the bank")
    country: str = Field(..., description="Country where the bank is located")


class AccountRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the account")
    bank: str = Field(..., description="Bank associated with the account")
    account_type: str = Field(
        Literal["savings", "credit-card", "investment"],
        description="Type of the account (e.g., savings, checking)"
    )
    balance: float = Field(..., description="Initial balance of the account")


class CategoryRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the category")


class TransactionRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the transaction")
    amount: float = Field(..., description="Transaction amount")
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    category: str = Field(..., description="Transaction category")
    account: str = Field(..., description="Account associated with the transaction")


class DeleteRequest(StrictBaseModel):
    table: str = Field(
        Literal["transactions", "categories", "accounts"],
        description="Table to delete from"
    )
    id: int = Field(..., description="ID to delete")


@app.post("/add-bank")
async def add_bank_api(payload: BankRequest) -> Dict[str, str]:
    """
    API endpoint to add a bank.

    Args:
        payload (Dict[str, str]): The bank details.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        response = await add_bank(payload.model_dump())
        return response
    except Exception as e:
        # Log the error if needed
        logger.error(f"[ERROR ADDING BANK]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/add-account")
async def add_account_api(payload: AccountRequest) -> Dict[str, str]:
    """
    API endpoint to add an account.

    Args:
        payload (AccountRequest): The account details.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        response = await add_account(payload.model_dump())
        return response
    except Exception as e:
        # Log the error if needed
        logger.error(f"[ERROR ADDING ACCOUNT]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/add-category")
async def add_category_api(payload: CategoryRequest) -> Dict[str, str]:
    """
    API endpoint to add a category.

    Args:
        payload (Dict[str, str]): The category details.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        response = await add_category(payload.model_dump())
        return response
    except Exception as e:
        # Log the error if needed
        logger.error(f"[ERROR ADDING CATEGORY]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/add-transaction")
async def add_transaction_api(payload: TransactionRequest) -> Dict[str, str]:
    """
    API endpoint to add a transaction.

    Args:
        payload (TransactionRequest): The transaction details.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        response = await add_transaction(payload.model_dump())
        return response
    except Exception as e:
        # Log the error if needed
        logger.error(f"[ERROR ADDING TRANSACTION]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/delete")
async def delete_api(payload: DeleteRequest) -> Dict[str, str]:
    """
    API endpoint to delete a row from specified table.

    Args:
        payload (Dict[str, int]): The ID to delete.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        response = await delete(payload.model_dump())
        return response
    except Exception as e:
        # Log the error if needed
        logger.error(f"[ERROR DELETING TRANSACTION]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def home_api():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    logger.info("Server is running at http://localhost:8000")