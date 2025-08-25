from typing import Dict, Literal, Any, Annotated, Union, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.database.banks import add_bank
from src.database.accounts import add_account
from src.database.categories import add_category
from src.database.common import delete
from src.database.transactions import (
    add_transaction,
    add_recurring_transaction,
    add_from_recurring
)
from src.utils.logger import logger
from src.views.networth import calculate_net_worth

app = FastAPI()


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class BankRequest(StrictBaseModel):
    entity: Literal["bank"]
    name: str = Field(..., description="Name of the bank")
    country: str = Field(..., description="Country where the bank is located")


class AccountRequest(StrictBaseModel):
    entity: Literal["account"]
    name: str = Field(..., description="Name of the account")
    bank: str = Field(..., description="Bank associated with the account")
    account_type: Literal["Savings", "Credit Card", "Investment"] = Field(
        ...,
        description="Type of the account (e.g., savings, checking)"
    )
    initial_balance: float = Field(..., description="Initial balance of the account")


class CategoryRequest(StrictBaseModel):
    entity: Literal["category"]
    name: str = Field(..., description="Name of the category")


class TransactionRequest(StrictBaseModel):
    entity: Literal["transaction"]
    name: str = Field(..., description="Name of the transaction")
    transaction_type: Literal["Income", "Expense"] = Field(
        ...,
        description="Type of the transaction (e.g., Income, Expense)"
    )
    amount: float = Field(..., description="Transaction amount")
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    category: str = Field(..., description="Transaction category")
    account: str = Field(..., description="Account associated with the transaction")


class RecurringTransactionRequest(StrictBaseModel):
    entity: Literal["recurring_transaction"]
    name: str = Field(..., description="Name of the recurring transaction")
    transaction_type: Literal["Income", "Expense"] = Field(
        ...,
        description="Type of the transaction (e.g., Income, Expense)"
    )
    amount: float = Field(..., description="Transaction amount")
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    frequency: Literal["Daily", "Weekly", "Monthly", "Yearly"] = Field(
        None,
        description="Frequency of the recurring transaction"
    )
    category: str = Field(..., description="Transaction category")
    account: Optional[str] = Field(None, description="Account associated with the transaction")


AddRequest = Annotated[
    Union[
        BankRequest,
        AccountRequest,
        CategoryRequest,
        TransactionRequest,
        RecurringTransactionRequest
    ],
    Field(discriminator="entity")
]


class DeleteRequest(StrictBaseModel):
    table: str = Field(
        Literal["transactions", "categories", "accounts"],
        description="Table to delete from"
    )
    id: int = Field(..., description="ID to delete")


class AddFromRecurringRequest(StrictBaseModel):
    recurring_transaction_id: int = Field(
        ..., description="ID of the recurring transaction to add"
    )
    date: str = Field(..., description="Date to add transactions for in YYYY-MM-DD format")
    amount: Optional[float] = Field(None, description="Optional amount to override")
    account: Optional[str] = Field(None, description="Optional account to override")


#########################################################
##################### GET ENDPOINTS #####################
#########################################################


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
        logger.error(f"[ERROR CALCULATING NET WORTH]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


#########################################################
##################### GET ENDPOINTS #####################
#########################################################


@app.post("/add")
async def add_api(payload: AddRequest) -> Dict[str, str]:
    """
    API endpoint to add a bank, account, category, or transaction.

    Args:
        payload (AddRequest): The details to add.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        if payload.entity == "bank":
            response = await add_bank(payload.model_dump())
        elif payload.entity == "account":
            response = await add_account(payload.model_dump())
        elif payload.entity == "category":
            response = await add_category(payload.model_dump())
        elif payload.entity == "transaction":
            response = await add_transaction(payload.model_dump())
        elif payload.entity == "recurring_transaction":
            response = await add_recurring_transaction(payload.model_dump())
        else:
            raise ValueError(f"Invalid entity: {payload.entity}")
        return response
    except Exception as e:
        logger.error(f"[ERROR ADDING {payload.entity.upper()}]: {e}")
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
        logger.error(f"[ERROR DELETING VALUE]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/add_from_recurring")
async def add_from_recurring_api(payload: AddFromRecurringRequest) -> Dict[str, str]:
    """
    API endpoint to add transactions from recurring transactions.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        response = await add_from_recurring(payload.model_dump())
        return response
    except Exception as e:
        logger.error(f"[ERROR ADDING FROM RECURRING TRANSACTIONS]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    logger.info("Server is running at http://localhost:8000")