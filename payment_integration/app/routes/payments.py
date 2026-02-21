from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..services.zenopay_service import create_purchase_order
from ..models import Transaction
from ..schemas import PurchaseRequest, PurchaseResponse
from fastapi import Query
from fastapi import Request
import requests
import os
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/purchase", response_model=PurchaseResponse)
def purchase_order(request: Request, db: Session = Depends(get_db),purchase: PurchaseRequest = None):
    print("Received purchase request:", purchase)  # Debugging line to check incoming request data
    result = create_purchase_order(purchase)
    print("Zenopay API response:", result)  # Debugging line to check API response

    print(result.get("order_id"))  # Debugging line to check API response   
    if not result.get("order_id"):
        raise HTTPException(status_code=400, detail="Failed to create purchase order")
    txn = Transaction(
        order_id=result["order_id"],
        status=result.get("status", "pending"),
        amount=purchase.amount,
        currency="TZS",
        provider="zenopay"
    )
    db.add(txn)
    db.commit()
    return result
    
@router.get("/payments/status")
def check_order_status(order_id: str = Query(...)):
    API_KEY = os.getenv("ZENOPAY_API_KEY")
    url = f"https://zenoapi.com/api/payments/order-status?order_id={order_id}"
    headers = {"x-api-key": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("resultcode") == "000":
            order = data["data"][0]
            return {
                "order_id": order["order_id"],
                "payment_status": order["payment_status"],
                "amount": order["amount"],
                "channel": order["channel"],
                "msisdn": order["msisdn"],
                "reference": order["reference"],
                "created": order["creation_date"]
            }
        else:
            return {"error": data.get("message")}
    except requests.RequestException as e:
        return {"error": str(e)}
