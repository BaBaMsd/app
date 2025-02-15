# from fastapi import APIRouter, HTTPException, Depends
# from services.client_service import create_client, get_client, get_clientslist
# from models.client import Client, ClientCreate
# from core.security import verify_token



# # ✅ Create a new client
# @router.post("/", response_model=Client)
# def create_new_client(client: ClientCreate, token: str = Depends(verify_token)):
#     new_client = create_client(client)
#     return new_client  # ✅ Return full client details

# # ✅ Get client balance
# @router.get("/{client_id}")
# def get_client_balance(client_id: int, token: str = Depends(verify_token)):
#     client = get_client(client_id)
#     if not client:
#         raise HTTPException(status_code=404, detail="Client not found")
#     return client

# # ✅ Get all clients
# @router.get("/list", response_model=list[Client])
# def get_clients(token: str = Depends(verify_token)):
#     return get_clientslist()


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from services.client_service import (
    get_client,
    get_clients_list,
    create_client,
    update_client,
    delete_client
)
from models.schemas import ClientCreate, ClientUpdate

router = APIRouter()

# ✅ Retrieve a single client by ID
@router.get("/{client_id}")
def get_client_info(client_id: int, db: Session = Depends(get_db)):
    client = get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

# ✅ Retrieve all clients
@router.get("/")
def get_all_clients(db: Session = Depends(get_db)):
    return get_clients_list(db)

# ✅ Create a new client
@router.post("/")
def register_client(client: ClientCreate, db: Session = Depends(get_db)):
    return create_client(db, client)

# ✅ Update an existing client
@router.put("/{client_id}")
def modify_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    updated_client = update_client(db, client_id, client_update)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated_client

# ✅ Delete a client
@router.delete("/{client_id}")
def remove_client(client_id: int, db: Session = Depends(get_db)):
    if not delete_client(db, client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}
