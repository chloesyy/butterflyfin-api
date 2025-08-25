import os
import pandas as pd
from typing import Dict, Any

from src.utils.logger import logger
from src.utils.db_utils import validate_value, ensure_id_first_column

async def add_account(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add an account to the DataFrame and save it to a CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing account details.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    payload.pop("entity")

    validate_value("banks", payload["bank"])

    df = pd.DataFrame([payload])
    df["id"] = 1
    df["balance"] = df["initial_balance"]

    if os.path.exists(os.path.join("data", "accounts.csv")):
        df_original = pd.read_csv(os.path.join("data", "accounts.csv"))

        if not df_original.empty:
            # Check for duplicate account names
            if payload["name"] in df_original["name"].values:
                raise ValueError(f"Account '{payload['name']}' already exists.")

            df["id"] = int(df_original["id"].max()) + 1
            df = pd.concat([df_original, df], ignore_index=True)

    df = ensure_id_first_column(df)

    df.to_csv(os.path.join("data", "accounts.csv"), index=False)
    logger.info("Account added successfully.")
    return {"message": "Account added successfully!"}


async def update_account_balance(account_name: str, amount: float) -> None:
    """
    Update the balance of an account in the DataFrame and save it to a CSV file.

    Args:
        account_name (str):
            The name of the account to update.
        amount (float):
            The new amount to add/subtract from the account.

    Returns:
        None
    """
    if not os.path.exists(os.path.join("data", "accounts.csv")):
        raise ValueError("There are no accounts available to update.")

    df = pd.read_csv(os.path.join("data", "accounts.csv"))
    if account_name not in df["name"].values:
        raise ValueError(f"Account '{account_name}' does not exist.")

    df.loc[df["name"] == account_name, "balance"] = (
        df.loc[df["name"] == account_name, "balance"] + amount
    )
    new_balance = df.loc[df["name"] == account_name, "balance"].values[0]

    df.to_csv(os.path.join("data", "accounts.csv"), index=False)
    logger.info(f"Updated balance for account '{account_name}' to {new_balance}.")
