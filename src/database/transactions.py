import os
import pandas as pd
from typing import Dict, Any

from src.database.accounts import update_account_balance
from src.utils.logger import logger
from src.utils.db_utils import validate_value, ensure_id_first_column

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
        if payload["transaction_type"] == "Income" else -payload["amount"]
    )

    df = pd.DataFrame([payload])
    df["id"] = 1

    if os.path.exists(os.path.join("data", "transactions.csv")):
        df_original = pd.read_csv(os.path.join("data", "transactions.csv"))

        if not df_original.empty:
            df["id"] = int(df_original["id"].max()) + 1
            df = pd.concat([df_original, df], ignore_index=True)

    df = ensure_id_first_column(df)

    # Update account balance
    await update_account_balance(payload["account"], payload["amount"])

    df.to_csv(os.path.join("data", "transactions.csv"), index=False)
    logger.info("Transaction added successfully.    ")
    return {"message": "Transaction added successfully!"}


async def add_recurring_transaction(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a recurring transaction to the DataFrame and save it to a CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing recurring transaction details.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    payload.pop("entity")

    # Validate values
    validate_value("categories", payload["category"])

    if payload["account"]:
        validate_value("accounts", payload["account"])

    if payload["amount"] <= 0:
        raise ValueError("Amount must be greater than zero.")

    # Adjust amount based on transaction type
    payload["amount"] = (
        payload["amount"]
        if payload["transaction_type"] == "Income" else -payload["amount"]
    )

    df = pd.DataFrame([payload])
    df["id"] = 1

    if os.path.exists(os.path.join("data", "recurring_transactions.csv")):
        df_original = pd.read_csv(os.path.join("data", "recurring_transactions.csv"))

        if not df_original.empty:
            if payload["name"] in df_original["name"].values:
                raise ValueError(f"Recurring transaction '{payload['name']}' already exists.")

            df["id"] = int(df_original["id"].max()) + 1
            df = pd.concat([df_original, df], ignore_index=True)

    df = ensure_id_first_column(df)

    df.to_csv(os.path.join("data", "recurring_transactions.csv"), index=False)
    logger.info("Recurring transaction added successfully.")
    return {"message": "Recurring transaction added successfully!"}


async def add_from_recurring(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a transaction from a recurring transaction to the DataFrame and save it to a CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing transaction details from a recurring transaction.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    # Validate values
    validate_value("recurring_transactions", payload["recurring_transaction_id"], col_name="id")
    df_recurring_transaction = pd.read_csv(os.path.join("data", "recurring_transactions.csv"))
    dict_recurring_transaction = (
        df_recurring_transaction[df_recurring_transaction["id"] == payload["recurring_transaction_id"]]
        .iloc[0]
        .to_dict()
    )

    if payload["account"]:
        validate_value("accounts", payload["account"])
        dict_recurring_transaction["account"] = payload["account"]

    if payload["amount"]:
        if payload["amount"] <= 0:
            raise ValueError("Amount must be greater than zero.")

        payload["amount"] = (
            payload["amount"]
            if payload["transaction_type"] == "income" else -payload["amount"]
        )
        dict_recurring_transaction["amount"] = payload["amount"]

    # Create new transaction dict
    dict_new_transaction = {
        "date": payload["date"],
        "name": dict_recurring_transaction["name"],
        "amount": dict_recurring_transaction["amount"],
        "category": dict_recurring_transaction["category"],
        "account": dict_recurring_transaction["account"],
        "transaction_type": dict_recurring_transaction["transaction_type"],
    }
    df = pd.DataFrame([dict_new_transaction])
    df["id"] = 1

    if os.path.exists(os.path.join("data", "transactions.csv")):
        df_original = pd.read_csv(os.path.join("data", "transactions.csv"))

        if not df_original.empty:
            df["id"] = int(df_original["id"].max()) + 1
            df = pd.concat([df_original, df], ignore_index=True)

    df = ensure_id_first_column(df)

    # Update account balance
    print("HIHI", dict_new_transaction)
    await update_account_balance(dict_new_transaction["account"], dict_new_transaction["amount"])

    df.to_csv(os.path.join("data", "transactions.csv"), index=False)
    logger.info("Transaction added successfully from recurring transaction.")
    return {"message": "Transaction added successfully from recurring transaction!"}