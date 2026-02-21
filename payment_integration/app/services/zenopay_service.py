import requests
import uuid
import os
from dotenv import load_dotenv
from loguru import logger

# Load environment from payment_integration/.env
load_dotenv()

API_URL = "https://zenoapi.com/api/payments/mobile_money_tanzania"
# Read and strip the API key to avoid accidental whitespace/newlines
API_KEY = os.getenv("ZENOPAY_API_KEY", "").strip()


def _mask_key(key: str) -> str:
    if not key:
        return "<not set>"
    k = key.strip()
    if len(k) <= 8:
        return "****"
    return f"{k[:4]}...{k[-4:]} (len={len(k)})"


def create_purchase_order(purchase):
    # Use provided order_id if present, otherwise generate one
    order_id = str(uuid.uuid4()) if not purchase.order_id else purchase.order_id
    payload = {
        "order_id": order_id,
        "buyer_email": purchase.buyer_email,
        "buyer_name": purchase.buyer_name,
        "buyer_phone": purchase.buyer_phone,
        "amount": purchase.amount,
        "webhook_url": purchase.webhook_url,
        "metadata": purchase.metadata or {}
    }

    logger.info("Creating purchase order: order_id={} buyer_email={} amount={}", order_id, purchase.buyer_email, purchase.amount)
    logger.debug("Using ZENOPAY_API_KEY: {}", _mask_key(API_KEY))

    if not API_KEY:
        logger.error("ZENOPAY_API_KEY is not configured in environment")
        return {"error": "ZENOPAY_API_KEY not configured"}

    headers = {"Content-Type": "application/json", "x-api-key": API_KEY}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        try:
            response.raise_for_status()
            logger.info("ZenoPay responded with status {}", response.status_code)
            try:
                return response.json()
            except Exception:
                logger.warning("ZenoPay returned non-JSON response body: {}", response.text)
                return {"result": response.text}
        except requests.HTTPError:
            try:
                body = response.json()
            except Exception:
                body = response.text
            logger.error("ZenoPay HTTP error: status={} body={}", response.status_code, body)
            return {"error": f"{response.status_code} {body}"}
    except requests.RequestException as e:
        resp = getattr(e, "response", None)
        if resp is not None:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            logger.error("RequestException with response: status={} body={}", resp.status_code, body)
            return {"error": f"{resp.status_code} {body}"}
        logger.exception("RequestException calling ZenoPay: {}", e)
        return {"error": str(e)}
