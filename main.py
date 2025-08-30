from typing import Dict, Literal, Any, Annotated, Union, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.database.banks import add_bank, delete_bank
from src.database.accounts import add_account, delete_account
from src.database.categories import add_category, delete_category
from src.database.transactions import (
    add_recurring_transaction,
    add_transaction,
    create_recurring_template,
    delete_transaction
)
from src.utils.logger import logger
from src.views.networth import calculate_net_worth

app = FastAPI()


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class AccountAddRequest(StrictBaseModel):
    task: Literal["add"]
    name: str = Field(..., description="Name of the account")
    bank: str = Field(..., description="Bank associated with the account")
    account_type: Literal["Savings", "Credit Card", "Investment"] = Field(
        ...,
        description="Type of the account (e.g., savings, checking)"
    )
    initial_balance: float = Field(..., description="Initial balance of the account")


class BankAddRequest(StrictBaseModel):
    task: Literal["add"]
    name: str = Field(..., description="Name of the bank")
    country: str = Field(..., description="Country where the bank is located")


class CategoryAddRequest(StrictBaseModel):
    task: Literal["add"]
    name: str = Field(..., description="Name of the category")


class TransactionAddRequest(StrictBaseModel):
    task: Literal["add"]
    name: str = Field(..., description="Name of the transaction")
    transaction_type: Literal["Income", "Expense"] = Field(
        ...,
        description="Type of the transaction (e.g., Income, Expense)"
    )
    amount: float = Field(..., description="Transaction amount")
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    category: str = Field(..., description="Transaction category")
    account: str = Field(..., description="Account associated with the transaction")


class TransactionCreateRecurringRequest(StrictBaseModel):
    task: Literal["create_recurring_template"]
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


class TransactionAddRecurringRequest(StrictBaseModel):
    task: Literal["add_recurring"]
    recurring_transaction_id: int = Field(
        ..., description="ID of the recurring transaction to add"
    )
    date: str = Field(..., description="Date to add transactions for in YYYY-MM-DD format")
    amount: Optional[float] = Field(None, description="Optional amount to override")
    account: Optional[str] = Field(None, description="Optional account to override")


class DeleteRequest(StrictBaseModel):
    task: Literal["delete"]
    id: int = Field(..., description="ID to delete")


AccountRequest = Annotated[
    Union[AccountAddRequest, DeleteRequest],
    Field(discriminator="task")
]


BankRequest = Annotated[
    Union[BankAddRequest, DeleteRequest],
    Field(discriminator="task")
]


CategoryRequest = Annotated[
    Union[CategoryAddRequest, DeleteRequest],
    Field(discriminator="task")
]


TransactionRequest = Annotated[
    Union[
        TransactionAddRequest,
        DeleteRequest,
        TransactionCreateRecurringRequest,
        TransactionAddRecurringRequest
    ],
    Field(discriminator="task")
]


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
        logger.error(f"[NET WORTH]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


#########################################################
##################### GET ENDPOINTS #####################
#########################################################

@app.post("/account")
async def account_api(payload: AccountRequest) -> Dict[str, Any]:
    """
    API endpoint to add an account.

    Args:
        payload (AccountRequest): The account details.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        if payload.task == "add":
            response = await add_account(payload.model_dump())
        elif payload.task == "delete":
            response = await delete_account(payload.model_dump())
        else:
            raise ValueError(f"Invalid task: {payload.task}")
        return response
    except Exception as e:
        logger.error(f"[ACCOUNT]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/bank")
async def bank_api(payload: BankRequest) -> Dict[str, Any]:
    """
    API endpoint to add a bank.

    Args:
        payload (BankRequest): The bank details.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        if payload.task == "add":
            response = await add_bank(payload.model_dump())
        elif payload.task == "delete":
            response = await delete_bank(payload.model_dump())
        else:
            raise ValueError(f"Invalid task: {payload.task}")
        return response
    except Exception as e:
        logger.error(f"[BANK]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/category")
async def category_api(payload: CategoryRequest) -> Dict[str, Any]:
    """
    API endpoint to add a category.

    Args:
        payload (CategoryRequest): The category details.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        if payload.task == "add":
            response = await add_category(payload.model_dump())
        elif payload.task == "delete":
            response = await delete_category(payload.model_dump())  # Uncomment when delete function is implemented
        else:
            raise ValueError(f"Invalid task: {payload.task}")
        return response
    except Exception as e:
        logger.error(f"[CATEGORY]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/transaction")
async def transaction_api(payload: TransactionRequest) -> Dict[str, Any]:
    """
    API endpoint to add a transaction.

    Args:
        payload (TransactionRequest): The transaction details.

    Returns:
        dict: A confirmation message indicating success.
    """
    try:
        if payload.task == "add":
            response = await add_transaction(payload.model_dump())
        elif payload.task == "delete":
            response = await delete_transaction(payload.model_dump())
        elif payload.task == "create_recurring_template":
            response = await create_recurring_template(payload.model_dump())
        elif payload.task == "add_recurring":
            response = await add_recurring_transaction(payload.model_dump())
        else:
            raise ValueError(f"Invalid task: {payload.task}")
        return response
    except Exception as e:
        logger.error(f"[TRANSACTION]: {e}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    logger.info("Server is running at http://localhost:8000")