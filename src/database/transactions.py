import os
import pandas as pd
from typing import Dict, Any

from src.database.accounts import update_account_balance
from src.utils.logger import logger
from src.utils.db_utils import validate_value

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
    # Validate values
    validate_value("categories", payload["category"])
    validate_value("accounts", payload["account"])
    if payload["amount"] <= 0:
        raise ValueError("Amount must be greater than zero.")
    payload["amount"] = (
        payload["amount"]
        if payload["transaction_type"] == "income" else -payload["amount"]
    )

    df = pd.DataFrame([payload])
    df["id"] = 1

    if os.path.exists(os.path.join("data", "transactions.csv")):
        df_original = pd.read_csv(os.path.join("data", "transactions.csv"))

        if not df_original.empty:
            df["id"] = int(df_original["id"].max()) + 1
            df = pd.concat([df_original, df], ignore_index=True)

    # Ensure 'id' is the first column
    cols = df.columns.tolist()
    if "id" in cols:
        cols.insert(0, cols.pop(cols.index("id")))
        df = df[cols]

    # Update account balance
    await update_account_balance(payload["account"], payload["amount"])

    df.to_csv(os.path.join("data", "transactions.csv"), index=False)
    logger.info("Transaction added successfully.    ")
    return {"message": "Transaction added successfully!"}
