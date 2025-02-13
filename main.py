from fastapi import FastAPI
from api.v1 import transactions, clients, merchants, agents, token
from core.security import verify_token

app = FastAPI()

# Ajouter les routes API
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(token.router, prefix="/token", tags=["Token"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
