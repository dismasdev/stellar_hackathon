import os
from elusion.zenopay import ZenoPay
from elusion.zenopay.models.order import NewOrder
from elusion.zenopay.utils import generate_id

# Create ZenoPay client using your environment variables
client = ZenoPay(
    account_id=os.getenv("ZENOPAY_ACCOUNT_ID"),
    api_key=os.getenv("ZENOPAY_API_KEY"),
    secret_key=os.getenv("ZENOPAY_SECRET_KEY")
)

def create_payment(amount: float, currency: str, buyer_email: str):
    order = NewOrder(
        order_id=generate_id(),
        buyer_email=buyer_email,
        amount=amount,
    )
    with client:
        response = client.orders.sync.create(order)
    return response
