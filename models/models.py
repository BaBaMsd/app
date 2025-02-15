from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

# ✅ User Model (Base Class)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # ✅ Added Name for Users
    phone_number = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    balance = Column(Float, default=0.0)  # ✅ Balance field

    # Polymorphic inheritance
    user_type = Column(String, nullable=False)  # 'client' or 'merchant'
    __mapper_args__ = {"polymorphic_identity": "user", "polymorphic_on": user_type}



# ✅ Client Model (inherits from User)
class Client(User):
    __tablename__ = "clients"
    id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    nni = Column(String, unique=True, nullable=False)  # ✅ Clients have an NNI

    __mapper_args__ = {"polymorphic_identity": "client"}

    transactions = relationship(
        "Transaction", back_populates="client", foreign_keys="[Transaction.client_id]"
    )


# ✅ Merchant Model (inherits from User)
class Merchant(User):
    __tablename__ = "merchants"  
    id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    code = Column(String, unique=True, index=True)  # ✅ Merchants have a unique code

    __mapper_args__ = {"polymorphic_identity": "merchant"}

    transactions = relationship(
        "Transaction", back_populates="merchant", foreign_keys="[Transaction.merchant_id]"
    )


# ✅ Transaction Model (Logs Every Payment)
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)  
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)  
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  
    timestamp = Column(DateTime, default=datetime.utcnow)

    # ✅ Relationships with Explicit Foreign Keys
    client = relationship("Client", back_populates="transactions", foreign_keys=[client_id])
    merchant = relationship("Merchant", back_populates="transactions", foreign_keys=[merchant_id])
