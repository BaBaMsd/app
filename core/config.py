import os

class Settings:
    PROJECT_NAME = "FastAPI Banking System"
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost/db_pay_odoo")
    SECRET_KEY = os.getenv("SECRET_KEY", "secretkey")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()
