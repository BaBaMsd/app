from sqlalchemy.orm import Session
from models.models import Transaction
from services.client_service import get_client
from services.merchant_service import get_merchant_by_code
from models.schemas import TransactionCreate
from typing import Optional

# ✅ Process a Payment Transaction
def process_payment(db: Session, transaction_data: TransactionCreate) -> Optional[dict]:
    # ✅ Fetch client
    client = get_client(db, transaction_data.client_id)
    if not client:
        return {"error": "Client not found"}

    # ✅ Fetch merchant by `merchant_code`
    merchant = get_merchant_by_code(db, transaction_data.merchant_code)
    if not merchant:
        return {"error": "Merchant not found"}

    # ✅ Check if client has enough balance
    if client.balance < transaction_data.amount:
        return {"error": "Insufficient funds"}

    # ✅ Deduct from client
    client.balance -= transaction_data.amount
    # ✅ Credit merchant
    merchant.balance += transaction_data.amount

    # ✅ Create transaction record
    transaction = Transaction(
        client_id=client.id,
        merchant_id=merchant.id,
        amount=transaction_data.amount,
        status="success"  
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "message": "Payment successful",
        "transaction_id": transaction.id,
        "client_new_balance": client.balance,
        "merchant_new_balance": merchant.balance
    }
