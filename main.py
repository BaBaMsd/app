from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models.database import Base, engine, get_db
from core.security import verify_token
from api.v1 import transactions, clients, merchants, token, facture, auth_routes
from models.models import User
from services.auth import get_current_user

# Initialiser la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Montre les fichiers statiques (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurer les templates
templates = Jinja2Templates(directory="templates2")

# Ajouter les routes API
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
app.include_router(token.router, prefix="/token", tags=["Token"])
app.include_router(auth_routes.router, prefix="", tags=["Authentication"])
app.include_router(facture.router, prefix="/odoo", tags=["Odoo"])

from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from services.auth import decode_access_token
from services.auth import get_user_by_id  # Import user retrieval function
from models.database import get_db
from sqlalchemy.orm import Session

@app.get("/home")
def home(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session")

    if not token:
        return RedirectResponse(url="/", status_code=303)  # Redirect to login if no session

    # Decode the token to get user data
    user_data = decode_access_token(token)
    if not user_data:
        return RedirectResponse(url="/", status_code=303)  # Redirect to login if token invalid

    # Fetch user from the database
    user = get_user_by_id(db, user_data["user_id"])
    if not user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse("home.html", {"request": request, "user": user})


def list_routes():
    print("\n📌 Liste des routes enregistrées dans l'application FastAPI :\n")
    for route in app.routes:
        print(f"📍 {route.path}")

if __name__ == "__main__":
    list_routes()  # Appelle la fonction pour afficher les routes dans le terminal
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8091)
