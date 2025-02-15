# from typing import List
# from fastapi import APIRouter, HTTPException, Depends
# from services.merchant_service import (
#     create_merchant, get_merchant, get_merchant_by_code,
#     get_merchantslist, update_merchant, delete_merchant
# )
# from models.merchant import Merchant, MerchantCreate, MerchantUpdate
# from core.security import verify_token

# router = APIRouter()

# # ✅ Create a new merchant
# @router.post("/", response_model=Merchant)
# def create_new_merchant(merchant: MerchantCreate, token: str = Depends(verify_token)):
#     new_merchant = create_merchant(merchant)
#     return new_merchant

# # ✅ Get a merchant by ID
# @router.get("/{merchant_id}", response_model=Merchant)
# def get_merchant_by_id(merchant_id: int, token: str = Depends(verify_token)):
#     merchant = get_merchant(merchant_id)
#     if not merchant:
#         raise HTTPException(status_code=404, detail="Merchant not found")
#     return merchant

# # ✅ Get a merchant by code
# @router.get("/code/{merchant_code}", response_model=Merchant)
# def get_merchant_by_code_api(merchant_code: str, token: str = Depends(verify_token)):
#     merchant = get_merchant_by_code(merchant_code)
#     if not merchant:
#         raise HTTPException(status_code=404, detail="Merchant not found")
#     return merchant

# # ✅ Get all merchants
# @router.get("/list", response_model=List[Merchant])
# def get_all_merchants(token: str = Depends(verify_token)):
#     return get_merchantslist()

# # ✅ Update a merchant
# @router.put("/{merchant_id}", response_model=Merchant)
# def update_existing_merchant(merchant_id: int, merchant_update: MerchantUpdate, token: str = Depends(verify_token)):
#     updated_merchant = update_merchant(merchant_id, merchant_update)
#     if not updated_merchant:
#         raise HTTPException(status_code=404, detail="Merchant not found")
#     return updated_merchant

# # ✅ Delete a merchant
# @router.delete("/{merchant_id}", response_model=dict)
# def delete_existing_merchant(merchant_id: int, token: str = Depends(verify_token)):
#     if delete_merchant(merchant_id):
#         return {"message": "Merchant deleted successfully"}
#     raise HTTPException(status_code=404, detail="Merchant not found")


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from services.merchant_service import (
    get_merchant,
    get_merchant_by_code,
    get_merchants_list,
    create_merchant,
    update_merchant,
    delete_merchant
)
from models.schemas import MerchantCreate, MerchantUpdate

router = APIRouter()

# ✅ Retrieve a single merchant by ID
@router.get("/{merchant_id}")
def get_merchant_info(merchant_id: int, db: Session = Depends(get_db)):
    merchant = get_merchant(db, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

# ✅ Retrieve a merchant by Code
@router.get("/code/{merchant_code}")
def get_merchant_by_code_info(merchant_code: str, db: Session = Depends(get_db)):
    merchant = get_merchant_by_code(db, merchant_code)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

# ✅ Retrieve all merchants
@router.get("/")
def get_all_merchants(db: Session = Depends(get_db)):
    return get_merchants_list(db)

# ✅ Create a new merchant
@router.post("/")
def register_merchant(merchant: MerchantCreate, db: Session = Depends(get_db)):
    return create_merchant(db, merchant)

# ✅ Update an existing merchant
@router.put("/{merchant_id}")
def modify_merchant(merchant_id: int, merchant_update: MerchantUpdate, db: Session = Depends(get_db)):
    updated_merchant = update_merchant(db, merchant_id, merchant_update)
    if not updated_merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return updated_merchant

# ✅ Delete a merchant
@router.delete("/{merchant_id}")
def remove_merchant(merchant_id: int, db: Session = Depends(get_db)):
    if not delete_merchant(db, merchant_id):
        raise HTTPException(status_code=404, detail="Merchant not found")
    return {"message": "Merchant deleted successfully"}
