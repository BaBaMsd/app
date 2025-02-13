from datetime import timedelta
from fastapi import APIRouter
from core.security import create_access_token
from core.config import settings

router = APIRouter()

# ✅ Route to generate a token without authentication
@router.get("/generate-token")
def generate_token():
    access_token = create_access_token(
        data={"message": "This is a test token"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
