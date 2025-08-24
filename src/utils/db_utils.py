import os
import pandas as pd
from typing import Any, Dict

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

    # Ensure 'id' is the first column
    cols = df.columns.tolist()
    if "id" in cols:
        cols.insert(0, cols.pop(cols.index("id")))
        df = df[cols]

    df.to_csv(os.path.join("data", f"{payload['table']}.csv"), index=False)
    logger.info(f"Deleted\n\n{to_delete.to_string(index=False)}\n")
    return {"message": "Deleted successfully!"}


def validate_value(table: str, value: str) -> bool:
    """
    Validate if the value in the payload exists in the table.
    Args:
        payload (Dict[str, Any]):
            A dictionary containing transaction details.

    Returns:
        (Bool):
            True if the category exists, otherwise raises a ValueError.
    """
    if not os.path.exists(os.path.join("data", f"{table}.csv")):
        raise ValueError(f"There are no {table} available. Please add it first.")

    df = pd.read_csv(os.path.join("data", f"{table}.csv"))
    if value not in df["name"].values:
        raise ValueError(f"'{value}' does not exist. Please add it to {table} first.")

    return True
