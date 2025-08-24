from typing import Dict, Literal, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.database.banks import add_bank
from src.database.accounts import add_account
from src.database.categories import add_category
from src.database.common import delete
from src.database.transactions import add_transaction
from src.utils.logger import logger
from src.views.networth import calculate_net_worth

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
        Literal["Savings", "Credit Card", "Investment"],
        description="Type of the account (e.g., savings, checking)"
    )
    initial_balance: float = Field(..., description="Initial balance of the account")


class CategoryRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the category")


class TransactionRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the transaction")
    transaction_type: str = Field(
        Literal["Income", "Expense"],
        description="Type of the transaction (e.g., income, expense)"
    )
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


@app.get("/networth")
async def networth_api() -> Dict[str, Any]:
    """
    API endpoint to get the net worth.

    Returns:
        dict: A dictionary containing the net worth.
    """
    try:
        output = await calculate_net_worth()
        return output
    except Exception as e:
        # Log the error if needed
        logger.error(f"[ERROR CALCULATING NET WORTH]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


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
        logger.error(f"[ERROR DELETING VALUE]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def home_api():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    logger.info("Server is running at http://localhost:8000")