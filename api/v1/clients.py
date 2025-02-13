from fastapi import APIRouter, HTTPException, Depends
from services.client_service import create_client, get_client, get_clientslist
from models.client import Client, ClientCreate
from core.security import verify_token

router = APIRouter()

# ✅ Create a new client
@router.post("/", response_model=Client)
def create_new_client(client: ClientCreate, token: str = Depends(verify_token)):
    new_client = create_client(client)
    return new_client  # ✅ Return full client details

# ✅ Get client balance
@router.get("/{client_id}")
def get_client_balance(client_id: int, token: str = Depends(verify_token)):
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

# ✅ Get all clients
@router.get("/list", response_model=list[Client])
def get_clients(token: str = Depends(verify_token)):
    return get_clientslist()
