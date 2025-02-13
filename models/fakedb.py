# Unified in-memory database
from typing import Dict


db: Dict[str, Dict[int, dict]] = {
    "clients": {},   # Store client data
    "merchants": {}  # Store merchant data
}

client_counter = 1   # Auto-increment ID for clients
merchant_counter = 1  # Auto-increment ID for merchants