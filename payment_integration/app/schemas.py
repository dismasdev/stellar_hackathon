from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

class PurchaseRequest(BaseModel):
    order_id: str
    buyer_email: EmailStr
    buyer_name: str
    buyer_phone: str
    amount: float
    webhook_url: Optional[str] = None
    metadata: Optional[Dict] = None

class PurchaseResponse(BaseModel):
    order_id: str
    status: Optional[str]
    error: Optional[str] = None
    
