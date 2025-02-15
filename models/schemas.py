from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ✅ User Schema (Base for Clients and Merchants)
class UserBase(BaseModel):
    phone_number: str
    name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    balance: float = 0.0  # ✅ Balance included at the User level

class UserCreate(UserBase):
    password: str
    user_type: str  # 'client' or 'merchant'

class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    balance: Optional[float] = None

class UserOut(UserBase):
    id: int

    model_config = {"from_attributes": True}  # ✅ Pydantic v2 compatibility

# ✅ Client Schema
class ClientBase(UserBase):
    user_type: str = "client"  
    nni: Optional[str] = None  

class ClientCreate(ClientBase, UserCreate):
    pass

class ClientUpdate(BaseModel):
    phone_number: Optional[str] = None
    name: Optional[str] = None
    nni: Optional[str] = None
    is_active: Optional[bool] = None
    balance: Optional[float] = None

class ClientOut(ClientBase, UserOut):
    pass

# ✅ Merchant Schema
class MerchantBase(UserBase):
    code: Optional[str] = None  
    user_type: str = "merchant"  

class MerchantCreate(MerchantBase, UserCreate):
    pass

class MerchantUpdate(BaseModel):
    phone_number: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    balance: Optional[float] = None
    code: Optional[str] = None

class MerchantOut(MerchantBase, UserOut):
    pass

# ✅ Transaction Schema
class TransactionBase(BaseModel):
    client_id: int
    amount: float
    status: Optional[str] = "pending"

class TransactionCreate(TransactionBase):
    merchant_code: str  # ✅ Ajout de `merchant_code`

class TransactionOut(TransactionBase):
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}
