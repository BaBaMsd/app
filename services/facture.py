import requests
from sqlalchemy.orm import Session
from models.models import Client, Transaction
from services.client_service import get_client_by_phone
from models.facture import OdooConfirmOrdersResponse, OdooOrder
from datetime import datetime
from typing import List, Optional

# ✅ Odoo Configuration
ODOO_URL = "http://localhost:8069/jsonrpc"
ODOO_DB = "demo"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

# ✅ Authenticate with Odoo
def odoo_authenticate():
    try:
        response = requests.post(ODOO_URL, json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}]
            },
            "id": 1
        })
        return response.json().get("result")
    except Exception as e:
        print(f"Error authenticating with Odoo: {e}")
        return None

# ✅ Get Unpaid Orders by Phone Number
def get_unpaid_orders_by_phone(db: Session, phone_number: str) -> OdooConfirmOrdersResponse:
    uid = odoo_authenticate()
    if not uid:
        return OdooConfirmOrdersResponse(message="Authentication failed", total_unpaid_value=0, orders=[])

    # ✅ Get client by phone number
    client = get_client_by_phone(db, phone_number)
    if not client:
        return OdooConfirmOrdersResponse(
            message=f"No client found with phone number: {phone_number}",
            total_unpaid_value=0,
            orders=[]
        )

    # ✅ Find the corresponding Odoo customer ID
    try:
        response = requests.post(ODOO_URL, json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner',
                    'search_read',
                    [[('phone', '=', phone_number)]],
                    {'fields': ['id'], 'limit': 1}
                ]
            },
            "id": 1
        })

        customer_data = response.json().get("result", [])
        if not customer_data:
            return OdooConfirmOrdersResponse(
                message=f"No customer found in Odoo with phone number: {phone_number}",
                total_unpaid_value=0,
                orders=[]
            )

        customer_id = customer_data[0]["id"]

        # ✅ Find unpaid orders
        response = requests.post(ODOO_URL, json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'sale.order',
                    'search_read',
                    [[('partner_id', '=', customer_id), ('state', '=', 'sent')]],
                    {'fields': ['id', 'state', 'amount_total']}
                ]
            },
            "id": 2
        })

        orders = response.json().get("result", [])
        if not orders:
            return OdooConfirmOrdersResponse(
                message=f"No unpaid orders found for {phone_number}",
                total_unpaid_value=0,
                orders=[]
            )

        total_unpaid_value = sum(order["amount_total"] for order in orders)
        return OdooConfirmOrdersResponse(
            message=f"Found {len(orders)} unpaid orders",
            total_unpaid_value=total_unpaid_value,
            orders=[OdooOrder(**order) for order in orders]
        )

    except Exception as e:
        return OdooConfirmOrdersResponse(message=f"Error fetching unpaid orders: {e}", total_unpaid_value=0, orders=[])

# ✅ Confirm Orders
def confirm_orders(db: Session, order_ids: List[int]) -> OdooConfirmOrdersResponse:
    uid = odoo_authenticate()
    if not uid:
        return OdooConfirmOrdersResponse(message="Authentication failed", total_unpaid_value=0, orders=[])

    if not order_ids:
        return OdooConfirmOrdersResponse(message="No orders to confirm", total_unpaid_value=0, orders=[])

    try:
        # ✅ Confirm Orders in Odoo
        requests.post(ODOO_URL, json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'sale.order',
                    'action_confirm',
                    [order_ids]
                ]
            },
            "id": 3
        })

        # ✅ Fetch Updated Orders
        response = requests.post(ODOO_URL, json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'sale.order',
                    'search_read',
                    [[('id', 'in', order_ids)]],
                    {'fields': ['id', 'state']}
                ]
            },
            "id": 4
        })

        updated_orders = response.json().get("result", [])
        return OdooConfirmOrdersResponse(
            message=f"Confirmed {len(order_ids)} orders",
            total_unpaid_value=0,
            orders=[OdooOrder(**order) for order in updated_orders]
        )

    except Exception as e:
        return OdooConfirmOrdersResponse(message=f"Error confirming orders: {e}", total_unpaid_value=0, orders=[])

# ✅ Process Payment and Confirm Orders
def process_payment_and_confirm_orders(db: Session, phone_number: str, order_ids: List[int]) -> dict:
    uid = odoo_authenticate()
    if not uid:
        return {"error": "Authentication with Odoo failed"}

    # ✅ Fetch client
    client = get_client_by_phone(db, phone_number)
    if not client:
        return {"error": "Client not found"}

    # ✅ Get unpaid orders
    unpaid_orders = get_unpaid_orders_by_phone(db, phone_number)
    if not unpaid_orders.orders:
        return {"error": "No unpaid orders found or incorrect order IDs"}

    total_order_value = sum(order.amount_total for order in unpaid_orders.orders if order.id in order_ids)

    # ✅ Check if client has enough balance
    if client.balance < total_order_value:
        return {"error": "Insufficient funds"}

    try:
        # ✅ Deduct balance and confirm orders
        client.balance -= total_order_value
        db.commit()

        # ✅ Confirm the orders in Odoo
        confirm_orders(db, order_ids)

        return {
            "message": "Payment processed and orders confirmed",
            "client_id": client.id,
            "phone_number": phone_number,
            "total_paid": total_order_value,
            "client_new_balance": client.balance,
            "confirmed_orders": order_ids
        }
    except Exception as e:
        return {"error": f"Failed to process payment: {e}"}
