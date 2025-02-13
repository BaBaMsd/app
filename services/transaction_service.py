from typing import Optional
from models.fakedb import db
from models.client import Client
from models.merchant import Merchant
from services.client_service import get_client
from services.merchant_service import get_merchant_by_code

# ✅ Process a Payment Transaction
def process_payment(client_id: int, merchant_code: str, amount: float) -> Optional[dict]:
    # Fetch client
    client = get_client(client_id)
    if not client:
        return {"error": "Client not found"}

    # Fetch merchant by code
    merchant = get_merchant_by_code(merchant_code)
    if not merchant:
        return {"error": "Merchant not found"}

    # Ensure client exists in db["clients"]
    if client_id not in db["clients"]:
        return {"error": f"Client with ID {client_id} does not exist"}

    # Ensure merchant exists in db["merchants"]
    if merchant.id not in db["merchants"]:
        return {"error": f"Merchant with ID {merchant.id} does not exist"}

    # Check if client has enough balance
    if client.balance < amount:
        return {"error": "Insufficient funds"}

    # Process the transaction
    db["clients"][client_id]["balance"] -= amount  # Deduct from client
    db["merchants"][merchant.id]["balance"] += amount  # Credit merchant

    return {
        "message": "Payment successful",
        "client_id": client_id,
        "merchant_code": merchant_code,
        "amount": amount,
        "client_new_balance": db["clients"][client_id]["balance"],
        "merchant_new_balance": db["merchants"][merchant.id]["balance"],
    }
