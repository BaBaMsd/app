from pydantic import BaseModel

# ✅ Payment Request Model
class PaymentRequest(BaseModel):
    client_id: int
    merchant_code: str
    amount: float
