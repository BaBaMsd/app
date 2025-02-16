# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from fastapi.security import OAuth2PasswordRequestForm
# from models.database import get_db
# from services.auth import register_user, login, get_current_user
# from models.schemas import UserCreate, UserOut

# router = APIRouter()

# # ✅ Register User
# @router.post("/register", response_model=UserOut)
# def register_user_route(user_data: UserCreate, db: Session = Depends(get_db)):
#     return register_user(db, user_data)

# # ✅ Login User (Returns JWT Token)
# @router.post("/login")
# def login_user_route(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
#     return login(db, form_data)

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import UserOut
from services.auth import get_current_user, login
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def login(request: Request,):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants invalides"})


# ✅ Connexion de l'utilisateur
@router.post("/login")
def login_user(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = login(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants invalides"})
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie("session", user.token)
    return response


# ✅ Get Current Logged-in User
@router.get("/me", response_model=UserOut)
def get_current_user_route(current_user: UserOut = Depends(get_current_user)):
    return current_user
