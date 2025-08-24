import logging
from colorlog import ColoredFormatter
from typing import Dict, Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.utils.logger import logger
from src.categories import add_category
from src.transactions import add_transaction
from src.utils.db_utils import delete

app = FastAPI()


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class CategoryRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the category")


class TransactionRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the transaction")
    amount: float = Field(..., description="Transaction amount")
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    category: str = Field(..., description="Transaction category")


class DeleteRequest(StrictBaseModel):
    table: str = Field(Literal["transactions", "categories"], description="Table to delete from")
    id: int = Field(..., description="ID to delete")


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
    API endpoint to delete a transaction.

    Args:
        payload (Dict[str, int]): The transaction ID to delete.

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