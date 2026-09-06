import os
from typing import Any

import razorpay
from dotenv import load_dotenv

load_dotenv()


RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")


if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    raise RuntimeError(
        "Razorpay credentials are missing. "
        "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env"
    )


client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)


def create_razorpay_order(
    amount: float,
    currency: str = "INR",
    receipt: str | None = None,
) -> dict[str, Any]:
    """
    Create a Razorpay Test Mode order.

    Razorpay expects amount in the smallest currency unit.
    For INR:
        ₹75,000 -> 7500000 paise
    """

    amount_in_paise = int(round(amount * 100))

    order_data: dict[str, Any] = {
        "amount": amount_in_paise,
        "currency": currency,
        "payment_capture": 1,
    }

    if receipt:
        order_data["receipt"] = receipt

    order = client.order.create(data=order_data)

    return {
        "id": order["id"],
        "entity": order.get("entity"),
        "amount": order["amount"],
        "currency": order["currency"],
        "status": order.get("status"),
        "receipt": order.get("receipt"),
    }