from fastapi import APIRouter, HTTPException, Depends
from services.transaction_service import process_payment
from core.security import verify_token
from models.transaction import PaymentRequest

router = APIRouter()

# ✅ Payment Route (using request body)
@router.post("/pay")
def pay_merchant(payment_data: PaymentRequest, token: str = Depends(verify_token)):
    result = process_payment(payment_data.client_id, payment_data.merchant_code, payment_data.amount)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
