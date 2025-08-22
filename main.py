import logging
from typing import Dict

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.transactions import add_transaction

logger = logging.getLogger("butterflyfin_api")
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s"
)

app = FastAPI()

class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"

class TransactionRequest(StrictBaseModel):
    name: str = Field(..., description="Name of the transaction")
    amount: float = Field(..., description="Amount of the transaction")
    date: str = Field(..., description="Date of the transaction in YYYY-MM-DD format")

@app.get("/")
def home_api():
    return {"message": "Hello, World!"}

@app.post("/add-transaction")
async def add_transaction_api(payload: TransactionRequest) -> Dict[str, str]:
    """
    API endpoint to add a transaction.
    
    Args:
        payload (TransactionRequest): The transaction details.
        
    Returns:
        dict: A confirmation message indicating success.
    """
    response = await add_transaction(payload.model_dump())
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    logger.info("Server is running at http://localhost:8000")