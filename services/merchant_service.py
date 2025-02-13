import random
from models.merchant import Merchant, MerchantCreate, MerchantUpdate
from models.fakedb import db, merchant_counter
from typing import Dict, List, Optional

# In-memory database (for testing purposes)
# merchants_db: Dict[int, dict] = {}  # Dictionary to store merchant data
# merchant_counter = 1  # Auto-incrementing ID counter

# ✅ Retrieve a single merchant by ID
def get_merchant(merchant_id: int) -> Optional[Merchant]:
    merchant_data = db.get(merchant_id)
    if merchant_data:
        return Merchant(**merchant_data)
    return None  # Return None if merchant does not exist

# ✅ Safe function to get a merchant by code
def get_merchant_by_code(code: str) -> Optional[Merchant]:
    for merchant_data in db["merchants"].values():
        if merchant_data.get("code") == code:  # ✅ Avoid KeyError
            return Merchant(**merchant_data)
    return None  # Return None if merchant does not exist


# ✅ Retrieve all merchants
def get_merchantslist() -> List[Merchant]:
    return [Merchant(**data) for data in db.values()]

def generate_unique_merchant_code() -> str:
    while True:
        code = str(random.randint(1000, 9999))  # Generate a 4-digit number
        if not any(merchant["code"] == code for merchant in db["merchants"].values()):
            return code  # Return if the code is unique

# ✅ Create a new merchant
def create_merchant(merchant: MerchantCreate) -> Merchant:
    global merchant_counter

    # Assign ID (auto-increment if not provided)
    merchant_id = merchant.id if merchant.id else merchant_counter
    if not merchant.id:
        merchant_counter += 1  # Increment only if ID was auto-generated

    # Generate a unique 4-digit code
    merchant_code = generate_unique_merchant_code()

    # Store merchant data
    merchant_data = merchant.model_dump()
    merchant_data["id"] = merchant_id
    merchant_data["code"] = merchant_code  # Assign generated code
    db["merchants"][merchant_id] = merchant_data  # Store in dictionary

    return Merchant(**merchant_data)  # # Return only stored data

# ✅ Update an existing merchant
def update_merchant(merchant_id: int, merchant_update: MerchantUpdate) -> Optional[Merchant]:
    merchant = db.get(merchant_id)
    if not merchant:
        return None  # Merchant not found

    update_data = merchant_update.model_dump(exclude_unset=True)  # Update only provided fields
    db[merchant_id].update(update_data)  # Apply updates

    return Merchant(**db[merchant_id])  # Return updated merchant

# ✅ Delete a merchant
def delete_merchant(merchant_id: int) -> bool:
    if merchant_id in db:
        del db[merchant_id]  # Remove merchant from the database
        return True
    return False  # Merchant not found
