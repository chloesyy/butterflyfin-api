import os
import pandas as pd
from typing import Dict, Any

from src.utils.logger import logger

def validate_category(payload: Dict[str, Any]) -> bool:
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
    if payload["category"] not in df["name"].values:
        raise ValueError(f"Category '{payload['category']}' does not exist. Please add it first.")

    return True


async def add_category(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a category to the DataFrame and save it to a CSV file.

    Args:
        payload (dict): A dictionary containing category details.

    Returns:
        dict: A confirmation message indicating success.
    """
    df_new_category = pd.DataFrame([payload])
    if os.path.exists(os.path.join("data", "categories.csv")):
        df = pd.read_csv(os.path.join("data", "categories.csv"))
        if payload["name"] in df["name"].values:
            raise ValueError(f"Category '{payload['category']}' already exists.")
        df = pd.concat([df, df_new_category], ignore_index=True)
    else:
        df = df_new_category
    
    df.to_csv(os.path.join("data", "categories.csv"), index=False)
    logger.info("Category added successfully.")
    return {"message": "Category added successfully!"}