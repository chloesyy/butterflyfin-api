import os
import pandas as pd
from typing import Dict, Any

from src.utils.logger import logger
from src.utils.db_utils import ensure_id_first_column


async def add_bank(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Add a bank to the DataFrame and save it to a CSV file.

    Args:
        payload (Dict[str, Any]):
            A dictionary containing bank details.

    Returns:
        (Dict[str, str]):
            A confirmation message indicating success.
    """
    payload.pop("entity")

    df = pd.DataFrame([payload])
    df["id"] = 1

    if os.path.exists(os.path.join("data", "banks.csv")):
        df_original = pd.read_csv(os.path.join("data", "banks.csv"))

        if not df_original.empty:
            # Check for duplicate bank names
            if payload["name"] in df_original["name"].values:
                raise ValueError(f"Bank '{payload['name']}' already exists.")

            df["id"] = int(df_original["id"].max()) + 1
            df = pd.concat([df_original, df], ignore_index=True)

    df = ensure_id_first_column(df)

    df.to_csv(os.path.join("data", "banks.csv"), index=False)
    logger.info("Bank added successfully.")
    return {"message": "Bank added successfully!"}