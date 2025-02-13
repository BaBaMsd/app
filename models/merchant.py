from pydantic import BaseModel
from typing import Optional

class MerchantBase(BaseModel):
    name: str
    balance: float = 0.0  # Default balance

class MerchantCreate(MerchantBase):
    id: Optional[int] = None
    code: Optional[int] = None

class MerchantUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    balance: Optional[float] = None

class Merchant(MerchantBase):
    id: int  # ID is required for returning merchant data
    code: int

    class Config:
        from_attributes = True  # For Pydantic v2 (Use `orm_mode = True` for v1)
