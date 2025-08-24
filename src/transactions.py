import os
import pandas as pd
from typing import Dict, Any

from src.utils.logger import logger
from src.categories import validate_category

async def add_transaction(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a transaction to the DataFrame and save it to a CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing transaction details.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    validate_category(payload)

    df_new_transaction = pd.DataFrame([payload])
    if os.path.exists(os.path.join("data", "transactions.csv")):
        df = pd.read_csv(os.path.join("data", "transactions.csv"))
        df = pd.concat([df, df_new_transaction], ignore_index=True)
    else:
        df = df_new_transaction

    df.to_csv(os.path.join("data", "transactions.csv"), index=False)
    logger.info("Transaction added successfully.    ")
    return {"message": "Transaction added successfully!"}
