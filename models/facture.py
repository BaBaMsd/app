from pydantic import BaseModel
from typing import List, Optional

class OdooProduct(BaseModel):
    id: int
    name: str
    list_price: float
    qty_available: int

class OdooOrder(BaseModel):
    id: int
    date_order: str
    amount_total: float

class OdooOrderSummary(BaseModel):
    day: str
    count: int
    total: float




# Models
class OdooConfirmOrdersRequest(BaseModel):
    email: str


class OdooConfirmOrdersResponse(BaseModel):
    message: str
    total_unpaid_value: float
    orders: List[OdooOrder]  

class OdooConfirmOrdersRequestClient(BaseModel):
    client_id: int
    merchant_code: str
    order_ids: List[int]

