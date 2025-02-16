from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models.database import Base, engine, get_db
from core.security import verify_token
from api.v1 import transactions, clients, merchants, token, facture, auth_routes

# Initialiser la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Montre les fichiers statiques (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurer les templates
templates = Jinja2Templates(directory="templates")

# Ajouter les routes API
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
app.include_router(token.router, prefix="/token", tags=["Token"])
app.include_router(auth_routes.router, prefix="/cauth", tags=["Authentication"])
app.include_router(facture.router, prefix="/odoo", tags=["Odoo"])

# ✅ Page d'accueil (accessible uniquement aux utilisateurs connectés)
@app.get("/")
def home(request: Request, db: Session = Depends(get_db), current_user=Depends(verify_token)):
    return templates.TemplateResponse("home.html", {"request": request, "user": current_user})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8091)
