import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

async def add_transaction(payload: dict) -> dict:
    """
    Add a transaction to the DataFrame and save it to a CSV file.

    Args:
        payload (dict): A dictionary containing transaction details.

    Returns:
        dict: A confirmation message indicating success.
    """
    df_new_transaction = pd.DataFrame([payload])
    if os.path.exists(os.path.join("data", "transactions.csv")):
        df = pd.read_csv(os.path.join("data", "transactions.csv"))
        df = pd.concat([df, df_new_transaction], ignore_index=True)
    else:
        df = df_new_transaction
    
    df.to_csv(os.path.join("data", "transactions.csv"), index=False)
    logger.info("Transaction added successfully.    ")
    return {"message": "Transaction added successfully!"}
