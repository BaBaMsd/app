from fastapi import Cookie, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import User
from models.schemas import UserCreate, UserOut
from core.security import verify_token

# Secret key for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ✅ Hash Password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ✅ Verify Password
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ✅ Generate JWT Token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")

        # Check if token has expired
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")

        return payload  # Returns the decoded token data

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Authenticate User
def authenticate_user(db: Session, phone_number: str, password: str):
    # ✅ Get user from the database
    user = db.query(User).filter(User.phone_number == phone_number).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    # ✅ Check password only if user exists
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    # ✅ Create JWT token
    token = create_access_token(data={"sub": user.phone_number, "user_id": user.id})

    return {"token": token, "token_type": "bearer"}

# ✅ Login Route
def login(db: Session, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect phone number or password")

    access_token = create_access_token(data={"sub": user.phone_number, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Register User
def register_user(db: Session, user_data: UserCreate):
    existing_user = db.query(User).filter(User.phone_number == user_data.phone_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    new_user = User(
        phone_number=user_data.phone_number,
        password=hash_password(user_data.password),
        is_active=True,
        is_superuser=False,
        balance=user_data.balance,
        user_type=user_data.user_type
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserOut.from_orm(new_user)


# Define OAuth2PasswordBearer to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ✅ Function to get current logged-in user
def get_current_user(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if not token:
        # 🔴 If no token is provided, check if it's in cookies
        token = request.cookies.get("session")
        if not token:
            raise HTTPException(status_code=401, detail="Token missing")

    # ✅ Decode the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # ✅ Fetch user from the database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user