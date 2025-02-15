# from models.client import Client, ClientCreate
# from models.fakedb import db, client_counter
# from typing import List, Optional

# # ✅ Function to retrieve a single client safely
# def get_client(client_id: int) -> Optional[Client]:
#     client_data = db["clients"].get(client_id)  # ✅ Fetch from db["clients"]
#     if client_data:
#         return Client(**client_data)
#     return None  # Return None if client does not exist

# # ✅ Function to retrieve all clients
# def get_clientslist() -> List[Client]:
#     return [Client(**data) for data in db["clients"].values()]  # ✅ Fetch from db["clients"]

# # ✅ Create a new client with auto-generated ID
# def create_client(client: ClientCreate) -> Client:
#     global client_counter

#     client_id = client.id if client.id else client_counter
#     if not client.id:
#         client_counter += 1  # Auto-increment ID

#     # Store client properly in db["clients"]
#     client_data = client.model_dump()
#     client_data["id"] = client_id
#     db["clients"][client_id] = client_data  # ✅ Store in db["clients"]

#     return Client(**client_data)

from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from models.models import Client
from models.schemas import ClientCreate, ClientUpdate
from typing import List, Optional

from services.auth import hash_password

# ✅ Retrieve a single client by ID
def get_client(db: Session, client_id: int) -> Optional[Client]:
    return db.query(Client).filter(Client.id == client_id).first()

# ✅ Retrieve all clients
def get_clients_list(db: Session) -> List[Client]:
    return db.query(Client).all()

def get_client_by_phone(db: Session, phone_number: str) -> Optional[Client]:
    return db.query(Client).filter(Client.phone_number == phone_number).first()

# ✅ Create a new client
def create_client(db: Session, client_data: ClientCreate) -> Client:
    new_client = Client(
        phone_number=client_data.phone_number,
        nni = client_data.nni,
        name= client_data.name,
        password=hash_password(client_data.password),
        balance=0.0,
        user_type="client"
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client  # Return stored data

# ✅ Update an existing client
def update_client(db: Session, client_id: int, client_update: ClientUpdate) -> Optional[Client]:
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return None  # Client not found

    update_data = client_update.model_dump(exclude_unset=True)  # Only update provided fields
    for key, value in update_data.items():
        setattr(client, key, value)  # Update client attributes dynamically

    db.commit()
    db.refresh(client)
    return client  # Return updated client

# ✅ Delete a client
def delete_client(db: Session, client_id: int) -> bool:
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
        return True  # Client successfully deleted
    return False  # Client not found


