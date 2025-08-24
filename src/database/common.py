import os
import pandas as pd
from typing import Dict, Any

from src.database.accounts import update_account_balance
from src.utils.logger import logger

async def delete(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Delete a transaction from the DataFrame and update the CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing transaction details.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    if not os.path.exists(os.path.join("data", f"{payload['table']}.csv")):
        raise ValueError(f"There are no {payload['table']} available to delete.")

    df = pd.read_csv(os.path.join("data", f"{payload['table']}.csv"))
    if payload["id"] not in df["id"].values:
        raise ValueError(f"ID '{payload['id']}' does not exist in {payload['table']}.")

    to_delete = df[df["id"] == payload["id"]]
    df = df[df["id"] != payload["id"]]

    # If deleting a transaction, update the account balance
    if payload["table"] == "transactions":
        await update_account_balance(
            to_delete.iloc[0]["account"], -to_delete.iloc[0]["amount"]
        )

    df.to_csv(os.path.join("data", f"{payload['table']}.csv"), index=False)
    logger.info(f"Deleted\n\n{to_delete.to_string(index=False)}\n")
    return {"message": "Deleted successfully!"}
