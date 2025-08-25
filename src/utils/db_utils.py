import os
import pandas as pd
from typing import Any, Dict

def validate_value(table: str, value: str, col_name: str = "name") -> bool:
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
        raise ValueError(f"There are no {table.replace('_', ' ')} available. Please add it first.")

    df = pd.read_csv(os.path.join("data", f"{table}.csv"))
    if value not in df[col_name].values:
        raise ValueError(f"'{value}' does not exist. Please add it to {table} first.")

    return True


def ensure_id_first_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure 'id' is the first column in the DataFrame.
    Args:
        df (pd.DataFrame): The DataFrame to modify.

    Returns:
        pd.DataFrame: The modified DataFrame with 'id' as the first column.
    """
    cols = df.columns.tolist()
    if "id" in cols:
        cols.insert(0, cols.pop(cols.index("id")))
        df = df[cols]
    return df
