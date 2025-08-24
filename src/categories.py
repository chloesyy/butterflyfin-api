import os
import pandas as pd
from typing import Dict, Any

from src.utils.logger import logger


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
                raise ValueError(f"Category '{payload['name']}' already exists.")

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
