import requests
from models.facture import OdooConfirmOrdersResponse, OdooProduct, OdooOrder, OdooOrderSummary
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models.fakedb import db, client_counter

from services.client_service import get_client
from services.merchant_service import get_merchant_by_code

# Odoo Configuration
ODOO_URL = "http://localhost:8069/jsonrpc"
ODOO_DB = "demo"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"

# Function to authenticate with Odoo
def odoo_authenticate():
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

# Get list of products
def get_odoo_products() -> List[OdooProduct]:
    uid = odoo_authenticate()
    if not uid:
        return []

    response = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.product',
                'search_read',
                [[('list_price', '>', 300)]],
                {'fields': ['id', 'name', 'list_price', 'qty_available'], 'limit': 10}
            ]
        },
        "id": 2
    })

    products = response.json().get("result", [])
    return [OdooProduct(**product) for product in products]

# Get weekly orders summary
def get_weekly_orders_summary() -> List[OdooOrderSummary]:
    uid = odoo_authenticate()
    if not uid:
        return []

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    start_date = start_of_week.strftime("%Y-%m-%d 00:00:00")
    end_date = end_of_week.strftime("%Y-%m-%d 23:59:59")

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
                [[('date_order', '>=', start_date), ('date_order', '<=', end_date)]],
                {'fields': ['id', 'date_order', 'amount_total'], 'limit': 1000}
            ]
        },
        "id": 3
    })

    orders = response.json().get("result", [])
    
    days_summary = {day: {"count": 0, "total": 0.0} for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}

    for order in orders:
        order_date = datetime.strptime(order["date_order"], "%Y-%m-%d %H:%M:%S")
        day_name = order_date.strftime("%A")
        days_summary[day_name]["count"] += 1
        days_summary[day_name]["total"] += order["amount_total"]

    return [OdooOrderSummary(day=day, count=summary["count"], total=summary["total"]) for day, summary in days_summary.items()]

def get_unpaid_orders(email: str):
    uid = odoo_authenticate()
    if not uid:
        raise ValueError("Authentication failed")

    # Trouver le client par email
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
                [[('email', '=', email)]],
                {'fields': ['id'], 'limit': 1}
            ]
        },
        "id": 1
    })

    customer_data = response.json().get("result", [])
    if not customer_data:
        return OdooConfirmOrdersResponse(message=f"No customer found with email: {email}", total_unpaid_value=0, orders=[])

    customer_id = customer_data[0]["id"]

    # Trouver les commandes non payées en état "sent"
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
        return OdooConfirmOrdersResponse(message=f"No unpaid orders found for {email}", total_unpaid_value=0, orders=[])

    total_unpaid_value = sum(order["amount_total"] for order in orders)
    return OdooConfirmOrdersResponse(
        message=f"Found {len(orders)} unpaid orders", 
        total_unpaid_value=total_unpaid_value, 
        orders=[OdooOrder(**order) for order in orders]
    )

def confirm_orders(order_ids: list):
    uid = odoo_authenticate()
    if not uid:
        raise ValueError("Authentication failed")

    if not order_ids:
        return OdooConfirmOrdersResponse(message="No orders to confirm", total_unpaid_value=0, orders=[])

    # Confirmer les commandes
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

    # Vérifier l'état des commandes mises à jour
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

# Payment processing and order confirmation
def process_payment_and_confirm_orders(client_id: int, merchant_code: str, order_ids: List[int]) -> Optional[dict]:
    # Fetch client
    client = get_client(client_id)
    if not client:
        return {"error": "Client not found"}

    # Fetch merchant by code
    merchant = get_merchant_by_code(merchant_code)
    if not merchant:
        return {"error": "Merchant not found"}

    # Ensure client exists in db["clients"]
    if client_id not in db["clients"]:
        return {"error": f"Client with ID {client_id} does not exist"}

    # Ensure merchant exists in db["merchants"]
    if merchant.id not in db["merchants"]:
        return {"error": f"Merchant with ID {merchant.id} does not exist"}

    # Authenticate with Odoo
    uid = odoo_authenticate()
    if not uid:
        raise ValueError("Authentication failed")

    # Retrieve orders and calculate total cost
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
                [[('id', 'in', order_ids), ('state', '=', 'sent')]],
                {'fields': ['id', 'state', 'amount_total']}
            ]
        },
        "id": 2
    })

    orders = response.json().get("result", [])
    if not orders:
        return {"error": "No unpaid orders found or incorrect order IDs"}

    total_order_value = sum(order["amount_total"] for order in orders)

    # Check if client has enough balance
    if client.balance < total_order_value:
        return {"error": "Insufficient funds"}

    # Deduct balance and credit merchant
    db["clients"][client_id]["balance"] -= total_order_value
    db["merchants"][merchant.id]["balance"] += total_order_value

    # Confirm the orders
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

    return {
        "message": "Payment processed and orders confirmed",
        "client_id": client_id,
        "merchant_code": merchant_code,
        "total_paid": total_order_value,
        "client_new_balance": db["clients"][client_id]["balance"],
        "merchant_new_balance": db["merchants"][merchant.id]["balance"],
        "confirmed_orders": order_ids
    }