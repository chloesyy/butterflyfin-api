import os
import pandas as pd

async def calculate_net_worth() -> float:
    """
    Calculate the total net worth by summing up all account balances.

    Returns:
        float: The total net worth.
    """
    if not os.path.exists(os.path.join("data", "accounts.csv")):
        return 0.0

    df = pd.read_csv(os.path.join("data", "accounts.csv"))
    if df.empty or "balance" not in df.columns:
        return 0.0

    total_net_worth = df["balance"].sum()
    
    type_breakdown = df.groupby("account_type")["balance"].sum().to_dict()
    return {
        "total_net_worth": total_net_worth,
        "type_breakdown": type_breakdown
    }