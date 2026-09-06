import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.database.client import supabase

router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"],
)


def verify_razorpay_signature(
    body: bytes,
    signature: str,
    secret: str,
) -> bool:
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


@router.post("/razorpay")
async def razorpay_webhook(request: Request) -> dict[str, Any]:
    # ---------------------------------------------------------
    # 1. Read raw request body
    # ---------------------------------------------------------
    body = await request.body()

    # ---------------------------------------------------------
    # 2. Read Razorpay headers
    # ---------------------------------------------------------
    signature = request.headers.get("X-Razorpay-Signature")
    event_id = request.headers.get("x-razorpay-event-id")

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay webhook signature.",
        )

    if not event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay webhook event ID.",
        )

    # ---------------------------------------------------------
    # 3. Load webhook secret
    # ---------------------------------------------------------
    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

    if not webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="RAZORPAY_WEBHOOK_SECRET is not configured.",
        )

    # ---------------------------------------------------------
    # 4. Verify webhook signature
    # ---------------------------------------------------------
    is_valid = verify_razorpay_signature(
        body=body,
        signature=signature,
        secret=webhook_secret,
    )

    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid Razorpay webhook signature.",
        )

    # ---------------------------------------------------------
    # 5. Parse JSON only AFTER signature verification
    # ---------------------------------------------------------
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload.",
        )

    event_type = payload.get("event")

    if not event_type:
        raise HTTPException(
            status_code=400,
            detail="Webhook event type is missing.",
        )

    # ---------------------------------------------------------
    # 6. Idempotency check
    # ---------------------------------------------------------
    existing_event_response = (
        supabase
        .table("webhook_events")
        .select("id, processed")
        .eq("event_id", event_id)
        .limit(1)
        .execute()
    )

    if existing_event_response.data:
        existing_event = existing_event_response.data[0]

        return {
            "success": True,
            "duplicate": True,
            "event_id": event_id,
            "processed": existing_event.get("processed", False),
            "message": "Webhook event already received.",
        }

    # ---------------------------------------------------------
    # 7. Store webhook event
    # ---------------------------------------------------------
    webhook_event_response = (
        supabase
        .table("webhook_events")
        .insert(
            {
                "event_id": event_id,
                "event_type": event_type,
                "provider": "razorpay",
                "payload": payload,
                "processed": False,
            }
        )
        .execute()
    )

    if not webhook_event_response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to store webhook event.",
        )

    webhook_event = webhook_event_response.data[0]

    # ---------------------------------------------------------
    # 8. Extract Razorpay payment/order information
    # ---------------------------------------------------------
    order_id = None
    payment_id = None
    payment_status = None

    razorpay_payment = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    razorpay_order = (
        payload
        .get("payload", {})
        .get("order", {})
        .get("entity", {})
    )

    if razorpay_payment:
        payment_id = razorpay_payment.get("id")
        order_id = razorpay_payment.get("order_id")
        payment_status = razorpay_payment.get("status")

    if razorpay_order and not order_id:
        order_id = razorpay_order.get("id")

    # ---------------------------------------------------------
    # 9. Only process successful payment events
    # ---------------------------------------------------------
    successful_events = {
        "payment.captured",
        "order.paid",
    }

    if event_type not in successful_events:
        processed_at = datetime.now(timezone.utc).isoformat()

        (
            supabase
            .table("webhook_events")
            .update(
                {
                    "processed": True,
                    "processed_at": processed_at,
                }
            )
            .eq("event_id", event_id)
            .execute()
        )

        return {
            "success": True,
            "event_id": event_id,
            "event_type": event_type,
            "processed": True,
            "message": "Webhook received but no transaction update was required.",
        }

    # ---------------------------------------------------------
    # 10. Validate Razorpay order ID
    # ---------------------------------------------------------
    if not order_id:
        raise HTTPException(
            status_code=400,
            detail="Razorpay order ID not found in webhook payload.",
        )

    # ---------------------------------------------------------
    # 11. Find our payment attempt
    # ---------------------------------------------------------
    payment_attempt_response = (
        supabase
        .table("payment_attempts")
        .select("*")
        .eq("provider", "razorpay")
        .eq("provider_payment_id", order_id)
        .limit(1)
        .execute()
    )

    if not payment_attempt_response.data:
        raise HTTPException(
            status_code=404,
            detail=(
                "No payment attempt found for Razorpay order "
                f"{order_id}."
            ),
        )

    payment_attempt = payment_attempt_response.data[0]

    transaction_id = payment_attempt["transaction_id"]

    # ---------------------------------------------------------
    # 12. Update payment attempt
    # ---------------------------------------------------------
    payment_update_data = {
        "status": "captured",
    }

    payment_attempt_update_response = (
        supabase
        .table("payment_attempts")
        .update(payment_update_data)
        .eq("id", payment_attempt["id"])
        .execute()
    )

    updated_payment_attempt = (
        payment_attempt_update_response.data[0]
        if payment_attempt_update_response.data
        else payment_attempt
    )

    # ---------------------------------------------------------
    # 13. Update transaction → PAID
    # ---------------------------------------------------------
    transaction_update_response = (
        supabase
        .table("transactions")
        .update(
            {
                "status": "paid",
            }
        )
        .eq("id", transaction_id)
        .execute()
    )

    if not transaction_update_response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to update transaction status.",
        )

    updated_transaction = transaction_update_response.data[0]

    # ---------------------------------------------------------
    # 14. Create audit log
    # ---------------------------------------------------------
    audit_response = (
        supabase
        .table("audit_logs")
        .insert(
            {
                "transaction_id": transaction_id,
                "action": "PAYMENT_WEBHOOK_VERIFIED",
                "details": {
                    "provider": "razorpay",
                    "event_id": event_id,
                    "event_type": event_type,
                    "order_id": order_id,
                    "payment_id": payment_id,
                    "payment_status": payment_status,
                    "source": "razorpay_webhook",
                },
            }
        )
        .execute()
    )

    # ---------------------------------------------------------
    # 15. Mark webhook event as processed
    # ---------------------------------------------------------
    processed_at = datetime.now(timezone.utc).isoformat()

    (
        supabase
        .table("webhook_events")
        .update(
            {
                "processed": True,
                "processed_at": processed_at,
            }
        )
        .eq("event_id", event_id)
        .execute()
    )

    return {
        "success": True,
        "event_id": event_id,
        "event_type": event_type,
        "processed": True,
        "transaction": updated_transaction,
        "payment_attempt": updated_payment_attempt,
        "audit_log": (
            audit_response.data[0]
            if audit_response.data
            else None
        ),
        "message": "Razorpay webhook processed successfully.",
    }