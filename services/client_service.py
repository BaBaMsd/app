from models.client import Client, ClientCreate
from models.fakedb import db, client_counter
from typing import List, Optional

# ✅ Function to retrieve a single client safely
def get_client(client_id: int) -> Optional[Client]:
    client_data = db["clients"].get(client_id)  # ✅ Fetch from db["clients"]
    if client_data:
        return Client(**client_data)
    return None  # Return None if client does not exist

# ✅ Function to retrieve all clients
def get_clientslist() -> List[Client]:
    return [Client(**data) for data in db["clients"].values()]  # ✅ Fetch from db["clients"]

# ✅ Create a new client with auto-generated ID
def create_client(client: ClientCreate) -> Client:
    global client_counter

    client_id = client.id if client.id else client_counter
    if not client.id:
        client_counter += 1  # Auto-increment ID

    # Store client properly in db["clients"]
    client_data = client.model_dump()
    client_data["id"] = client_id
    db["clients"][client_id] = client_data  # ✅ Store in db["clients"]

    return Client(**client_data)
