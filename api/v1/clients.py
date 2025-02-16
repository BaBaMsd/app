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

from fastapi import APIRouter, Depends, HTTPException, Form, Body, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models.database import get_db
from services.client_service import create_client, get_client_by_phone, get_client_by_nni
from models.schemas import ClientCreate
import re

router = APIRouter()

# ✅ Validation des numéros Mauritaniens (8 chiffres, commence par 2, 3 ou 4)
def validate_phone_number(phone_number: str):
    if not re.match(r"^[234]\d{7}$", phone_number):
        raise HTTPException(status_code=400, detail="Numéro de téléphone invalide (doit contenir 8 chiffres et commencer par 2, 3 ou 4)")

# ✅ Validation du NNI (10 chiffres)
def validate_nni(nni: str):
    if not re.match(r"^\d{10}$", nni):
        raise HTTPException(status_code=400, detail="NNI invalide (doit contenir exactement 10 chiffres)")

# ✅ Create a new client (supporte JSON et Form)
@router.post("/")
def register_client(
    request: Request,
    db: Session = Depends(get_db),
    client_json: ClientCreate = Body(None),  # JSON support
    name: str = Form(None),
    phone_number: str = Form(None),
    password: str = Form(None),
    nni: str = Form(None),
):
    if client_json:  # Si JSON est envoyé
        name = client_json.name
        phone_number = client_json.phone_number
        password = client_json.password
        nni = client_json.nni

    # ✅ Vérifier si tous les champs sont fournis
    if not all([name, phone_number, password, nni]):
        raise HTTPException(status_code=400, detail="Tous les champs sont obligatoires")

    # ✅ Valider le numéro de téléphone
    validate_phone_number(phone_number)

    # ✅ Valider le NNI
    validate_nni(nni)

    # ✅ Vérifier si le numéro de téléphone existe déjà
    if get_client_by_phone(db, phone_number):
        raise HTTPException(status_code=400, detail="Numéro de téléphone déjà utilisé")

    # ✅ Vérifier si le NNI existe déjà
    if get_client_by_nni(db, nni):
        raise HTTPException(status_code=400, detail="NNI déjà utilisé")

    # ✅ Créer le client
    client_data = ClientCreate(
        name=name,
        phone_number=phone_number,
        password=password,
        nni=nni
    )
    new_client = create_client(db, client_data)

    # ✅ Redirection vers la page de connexion après inscription
    return RedirectResponse(url="/", status_code=303)



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
# @router.post("/")
# def register_client(client: ClientCreate, db: Session = Depends(get_db)):
#     return create_client(db, client)

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
