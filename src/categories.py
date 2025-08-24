import os
import pandas as pd
from typing import Dict, Any

from src.utils.logger import logger

def validate_category(category: str) -> bool:
    """
    Validate if the category in the payload exists in the categories CSV.
    Args:
        payload (Dict[str, Any]):
            A dictionary containing transaction details.

    Returns:
        (Bool):
            True if the category exists, otherwise raises a ValueError.
    """
    if not os.path.exists(os.path.join("data", "categories.csv")):
        raise ValueError("There are no categories available. Please add a category first.")

    df = pd.read_csv(os.path.join("data", "categories.csv"))
    if category not in df["name"].values:
        raise ValueError(f"Category '{category}' does not exist. Please add it first.")

    return True


async def add_category(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a category to the DataFrame and save it to a CSV file.

    Args:
        payload (dict): A dictionary containing category details.

    Returns:
        dict: A confirmation message indicating success.
    """
    df = pd.DataFrame([payload])
    df["id"] = 1

    if os.path.exists(os.path.join("data", "categories.csv")):
        df_original = pd.read_csv(os.path.join("data", "categories.csv"))

        if not df_original.empty:
            # Check for duplicate category names
            if payload["name"] in df_original["name"].values:
                raise ValueError(f"Category '{payload['category']}' already exists.")

            df["id"] = int(df_original["id"].max()) + 1
            df = pd.concat([df_original, df], ignore_index=True)

    # Ensure 'id' is the first column
    cols = df.columns.tolist()
    if "id" in cols:
        cols.insert(0, cols.pop(cols.index("id")))
        df = df[cols]

    df.to_csv(os.path.join("data", "categories.csv"), index=False)
    logger.info("Category added successfully.")
    return {"message": "Category added successfully!"}
