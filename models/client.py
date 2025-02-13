from pydantic import BaseModel
from typing import Optional, List

class ClientBase(BaseModel):
    name: str
    balance: float = 0.0  # Default balance

class ClientCreate(ClientBase):
    id: Optional[int] = None  # ID is optional for new clients

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    balance: Optional[float] = None

class Client(ClientBase):
    id: int  # ID is required for returning client data

    class Config:
        from_attributes = True