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
    payload.pop("task")

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
    new_balance = await update_account_balance(payload["account"], payload["amount"])

    df.to_csv(os.path.join("data", "transactions.csv"), index=False)
    logger.info("[TRANSACTION] Transaction added successfully.")
    return {
        "added_transaction": df.iloc[-1].to_dict(),
        "new_balance": new_balance
    }


async def delete_transaction(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Delete a transaction from the DataFrame and update the CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing transaction details.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    if not os.path.exists(os.path.join("data", "transactions.csv")):
        raise ValueError(f"There are no transactions available to delete.")

    df = pd.read_csv(os.path.join("data", "transactions.csv"))
    if payload["id"] not in df["id"].values:
        raise ValueError(f"ID '{payload['id']}' does not exist in transactions.")

    to_delete = df[df["id"] == payload["id"]]
    df = df[df["id"] != payload["id"]]

    # If deleting a transaction, update the account balance
    new_balance = await update_account_balance(
        to_delete.iloc[0]["account"], -to_delete.iloc[0]["amount"]
    )

    df.to_csv(os.path.join("data", "transactions.csv"), index=False)
    logger.info(f"[TRANSACTION] Deleted\n\n{to_delete.to_string(index=False)}\n")
    return {
        "deleted_transaction": to_delete.iloc[0].to_dict(),
        "new_balance": new_balance
    }


async def create_recurring_template(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a recurring transaction to the DataFrame and save it to a CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing recurring transaction details.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    payload.pop("task")

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
    logger.info("[TRANSACTION] Recurring transaction added successfully.")
    return {"added_recurring_transaction": df.iloc[-1].to_dict()}


async def add_recurring_transaction(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a transaction from a recurring transaction to the DataFrame and save it to a CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing transaction details from a recurring transaction.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    payload.pop("task")

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
        "task": "add",
        "date": payload["date"],
        "name": dict_recurring_transaction["name"],
        "amount": dict_recurring_transaction["amount"],
        "category": dict_recurring_transaction["category"],
        "account": dict_recurring_transaction["account"],
        "transaction_type": dict_recurring_transaction["transaction_type"],
    }

    result = await add_transaction(dict_new_transaction)
    logger.info("[TRANSACTION] Transaction added successfully from recurring transaction.")
    return result