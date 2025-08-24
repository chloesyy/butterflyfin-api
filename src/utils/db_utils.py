import os
import pandas as pd
from typing import Any, Dict

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
