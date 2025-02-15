# """ from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.responses import JSONResponse, HTMLResponse
# from fastapi.templating import Jinja2Templates
# import requests
# from datetime import datetime, timedelta

# # Initialize FastAPI app
# app = FastAPI()

# # Templates directory for HTML rendering
# templates = Jinja2Templates(directory="templates")

# # Odoo Configuration
# ODOO_URL = "http://localhost:8069/jsonrpc"
# ODOO_DB = "demo"
# ODOO_USERNAME = "admin"
# ODOO_PASSWORD = "admin"

# # 🔹 Function to authenticate with Odoo
# def odoo_authenticate():
#     response = requests.post(ODOO_URL, json={
#         "jsonrpc": "2.0",
#         "method": "call",
#         "params": {
#             "service": "common",
#             "method": "authenticate",
#             "args": [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}]
#         },
#         "id": 1
#     })
#     return response.json().get("result")


# # 🔹 Fetch products from Odoo
# @app.get("/products")
# def get_products():
#     uid = odoo_authenticate()
#     if not uid:
#         raise HTTPException(status_code=401, detail="Authentication failed")

#     response = requests.post(ODOO_URL, json={
#         "jsonrpc": "2.0",
#         "method": "call",
#         "params": {
#             "service": "object",
#             "method": "execute_kw",
#             "args": [
#                 ODOO_DB, uid, ODOO_PASSWORD,
#                 'product.product',
#                 'search_read',
#                 [[('list_price', '>', 300)]],
#                 {'fields': ['id', 'name', 'list_price', 'qty_available'], 'limit': 10}
#             ]
#         },
#         "id": 2
#     })

#     return response.json().get("result", [])


# # 🔹 Fetch weekly orders summary
# @app.get("/weekly_orders_summary")
# def weekly_orders_summary():
#     uid = odoo_authenticate()
#     if not uid:
#         raise HTTPException(status_code=401, detail="Authentication failed")

#     today = datetime.now()
#     start_of_week = today - timedelta(days=today.weekday())
#     end_of_week = start_of_week + timedelta(days=6)

#     start_date = start_of_week.strftime("%Y-%m-%d 00:00:00")
#     end_date = end_of_week.strftime("%Y-%m-%d 23:59:59")

#     response = requests.post(ODOO_URL, json={
#         "jsonrpc": "2.0",
#         "method": "call",
#         "params": {
#             "service": "object",
#             "method": "execute_kw",
#             "args": [
#                 ODOO_DB, uid, ODOO_PASSWORD,
#                 'sale.order',
#                 'search_read',
#                 [[('date_order', '>=', start_date), ('date_order', '<=', end_date)]],
#                 {'fields': ['id', 'date_order', 'amount_total'], 'limit': 1000}
#             ]
#         },
#         "id": 4
#     })

#     orders = response.json().get("result", [])

#     days_summary = {
#         day: {"count": 0, "total": 0.0}
#         for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#     }

#     for order in orders:
#         order_date = datetime.strptime(order["date_order"], "%Y-%m-%d %H:%M:%S")
#         day_name = order_date.strftime("%A")
#         days_summary[day_name]["count"] += 1
#         days_summary[day_name]["total"] += order["amount_total"]

#     summaries = [{"day": day, "count": summary["count"], "total": summary["total"]}
#                  for day, summary in days_summary.items()]

#     return templates.TemplateResponse("weekly_summary.html", {"request": {}, "summaries": summaries})


# # 🔹 Confirm unpaid orders for a customer
# @app.post("/confirm_unpaid_orders")
# def confirm_unpaid_orders(email: str):
#     uid = odoo_authenticate()
#     if not uid:
#         raise HTTPException(status_code=401, detail="Authentication failed")

#     response = requests.post(ODOO_URL, json={
#         "jsonrpc": "2.0",
#         "method": "call",
#         "params": {
#             "service": "object",
#             "method": "execute_kw",
#             "args": [
#                 ODOO_DB, uid, ODOO_PASSWORD,
#                 'res.partner',
#                 'search_read',
#                 [[('email', '=', email)]],
#                 {'fields': ['id'], 'limit': 1}
#             ]
#         },
#         "id": 1
#     })

#     customer_data = response.json().get("result", [])
#     if not customer_data:
#         raise HTTPException(status_code=404, detail=f"No customer found with email: {email}")

#     customer_id = customer_data[0]["id"]

#     response = requests.post(ODOO_URL, json={
#         "jsonrpc": "2.0",
#         "method": "call",
#         "params": {
#             "service": "object",
#             "method": "execute_kw",
#             "args": [
#                 ODOO_DB, uid, ODOO_PASSWORD,
#                 'sale.order',
#                 'search_read',
#                 [[('partner_id', '=', customer_id), ('state', '=', 'sent')]],
#                 {'fields': ['id', 'state', 'amount_total']}
#             ]
#         },
#         "id": 2
#     })

#     orders = response.json().get("result", [])
#     if not orders:
#         return {"message": f"No unpaid orders found for {email}"}

#     order_ids = [order["id"] for order in orders]

#     response = requests.post(ODOO_URL, json={
#         "jsonrpc": "2.0",
#         "method": "call",
#         "params": {
#             "service": "object",
#             "method": "execute_kw",
#             "args": [
#                 ODOO_DB, uid, ODOO_PASSWORD,
#                 'sale.order',
#                 'action_confirm',
#                 [order_ids]
#             ]
#         },
#         "id": 3
#     })

#     return {"message": f"Confirmed {len(order_ids)} orders", "orders": order_ids}


# # 🔹 Render a simple form
# @app.get("/form", response_class=HTMLResponse)
# def show_form(request: Request):
#     return templates.TemplateResponse("form.html", {"request": request})


#  """




# from fastapi import APIRouter, HTTPException
# from services.facture import confirm_orders, get_odoo_products, get_unpaid_orders , get_weekly_orders_summary, process_payment_and_confirm_orders
# from models.facture import OdooConfirmOrdersRequest, OdooConfirmOrdersRequestClient, OdooConfirmOrdersResponse, OdooProduct, OdooOrderSummary
# from typing import List

# router = APIRouter()

# @router.get("/products", response_model=List[OdooProduct])
# def get_products():
#     """Fetch products from Odoo"""
#     return get_odoo_products()

# @router.get("/weekly_orders_summary", response_model=List[OdooOrderSummary])
# def weekly_orders_summary():
#     """Fetch weekly sales order summary"""
#     return get_weekly_orders_summary()


# @router.post("/get_unpaid_orders", response_model=OdooConfirmOrdersResponse)
# def get_unpaid_orders_route(request: OdooConfirmOrdersRequest):
#     try:
#         return get_unpaid_orders(request.email)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.post("/confirm_orders", response_model=OdooConfirmOrdersResponse)
# def confirm_orders_route(order_ids: List[int]):
#     try:
#         return confirm_orders(order_ids)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
    

# @router.post("/process_payment_and_confirm_orders", response_model=dict)
# def process_payment_and_confirm_orders_route(request: OdooConfirmOrdersRequestClient):
#     try:
#         return process_payment_and_confirm_orders(request.client_id, request.merchant_code, request.order_ids)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))





from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from services.facture import get_unpaid_orders_by_phone, confirm_orders, process_payment_and_confirm_orders
from models.facture import OdooConfirmOrdersResponse
from services.auth import get_current_user

router = APIRouter(prefix="/facture", tags=["Facture"])

# ✅ Get unpaid orders for authenticated user
@router.get("/unpaid_orders", response_model=OdooConfirmOrdersResponse)
def get_unpaid_orders_route(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return get_unpaid_orders_by_phone(db, current_user.phone_number)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Confirm orders
@router.post("/confirm_orders")
def confirm_orders_route(order_ids: List[int], db: Session = Depends(get_db)):
    try:
        return confirm_orders(db, order_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Process Payment & Confirm Orders
@router.post("/process_payment_and_confirm_orders")
def process_payment_and_confirm_orders_route(order_ids: List[int], db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return process_payment_and_confirm_orders(db, current_user.phone_number, order_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
