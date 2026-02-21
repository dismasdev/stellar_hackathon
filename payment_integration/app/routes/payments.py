from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.zenopay_service import create_payment
from app.models import Transaction

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/payments")
def create_order(amount: float, email: str, db: Session = Depends(get_db)):
    result = create_payment(amount, "USD", email)

    txn = Transaction(
        order_id=result.order_id,
        status=result.payment_status,
        amount=amount,
        currency="USD",
        provider="zenopay"
    )
    db.add(txn)
    db.commit()
    return {"order": result}
