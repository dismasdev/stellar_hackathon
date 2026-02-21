from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    status = Column(String)
    amount = Column(Float)
    currency = Column(String)
    provider = Column(String)
