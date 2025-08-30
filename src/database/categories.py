import os
import pandas as pd
from typing import Dict, Any

from src.utils.logger import logger
from src.utils.db_utils import ensure_id_first_column


async def add_category(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a category to the DataFrame and save it to a CSV file.

    Args:
        payload (dict): A dictionary containing category details.

    Returns:
        dict: A confirmation message indicating success.
    """
    payload.pop("task")

    df = pd.DataFrame([payload])
    df["id"] = 1

    if os.path.exists(os.path.join("data", "categories.csv")):
        df_original = pd.read_csv(os.path.join("data", "categories.csv"))

        if not df_original.empty:
            # Check for duplicate category names
            if payload["name"] in df_original["name"].values:
                raise ValueError(f"Category '{payload['name']}' already exists.")

            df["id"] = int(df_original["id"].max()) + 1
            df = pd.concat([df_original, df], ignore_index=True)

    df = ensure_id_first_column(df)

    df.to_csv(os.path.join("data", "categories.csv"), index=False)
    logger.info("[CATEGORY] Category added successfully.")
    return {"added_category": df.iloc[-1].to_dict()}


async def delete_category(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Delete a transaction from the DataFrame and update the CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing transaction details.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    if not os.path.exists(os.path.join("data", "categories.csv")):
        raise ValueError("No categories available to delete.")

    df = pd.read_csv(os.path.join("data", "categories.csv"))
    if payload["id"] not in df["id"].values:
        raise ValueError(f"ID '{payload['id']}' does not exist in the category database.")

    to_delete = df[df["id"] == payload["id"]]
    df = df[df["id"] != payload["id"]]

    df.to_csv(os.path.join("data", "categories.csv"), index=False)
    logger.info(f"[CATEGORY] Deleted\n\n{to_delete.to_string(index=False)}\n")
    return {"deleted_category": to_delete.iloc[0].to_dict()}

