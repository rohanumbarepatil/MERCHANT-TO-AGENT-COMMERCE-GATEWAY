from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.client import supabase
from app.services.razorpay import (
    RAZORPAY_KEY_ID,
    client,
    create_razorpay_order,
)


router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"],
)


# =========================================================
# REQUEST SCHEMAS
# =========================================================

class PaymentRequest(BaseModel):
    transaction_id: str


class PaymentVerificationRequest(BaseModel):
    transaction_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# =========================================================
# AUDIT HELPER
# =========================================================

def create_audit_log(
    transaction_id: str,
    action: str,
    details: dict[str, Any],
) -> dict[str, Any]:
    """
    Creates an audit record for the transaction.
    """

    audit_data = {
        "transaction_id": transaction_id,
        "action": action,
        "details": details,
    }

    response = (
        supabase
        .table("audit_logs")
        .insert(audit_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Audit log creation failed.",
        )

    return response.data[0]


# =========================================================
# CREATE RAZORPAY ORDER
# =========================================================

@router.post("/")
def process_payment(
    request: PaymentRequest,
) -> dict[str, Any]:

    # -----------------------------------------------------
    # 1. Fetch transaction
    # -----------------------------------------------------

    transaction_response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("id", request.transaction_id)
        .limit(1)
        .execute()
    )

    if not transaction_response.data:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    transaction = transaction_response.data[0]

    transaction_id = transaction["id"]
    transaction_status = transaction.get("status")
    amount = float(transaction["amount"])
    currency = transaction.get("currency", "INR")

    # -----------------------------------------------------
    # 2. Prevent duplicate payment
    # -----------------------------------------------------

    if transaction_status == "paid":
        raise HTTPException(
            status_code=400,
            detail=(
                "Payment cannot be processed for "
                "transaction status: paid"
            ),
        )

    # -----------------------------------------------------
    # 3. Only approved transactions can be paid
    # -----------------------------------------------------

    if transaction_status != "approved":
        raise HTTPException(
            status_code=400,
            detail=(
                "Payment cannot be processed for "
                f"transaction status: {transaction_status}"
            ),
        )

    # -----------------------------------------------------
    # 4. Create Razorpay order
    # -----------------------------------------------------

    try:
        razorpay_order = create_razorpay_order(
            amount=amount,
            currency=currency,
            receipt=f"txn_{transaction_id[:8]}",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Razorpay order creation failed: "
                f"{str(exc)}"
            ),
        )

    razorpay_order_id = razorpay_order["id"]

    # -----------------------------------------------------
    # 5. Create payment attempt
    # -----------------------------------------------------

    payment_attempt_data = {
        "transaction_id": transaction_id,
        "provider": "razorpay",
        "provider_payment_id": razorpay_order_id,
        "status": "created",
    }

    payment_attempt_response = (
        supabase
        .table("payment_attempts")
        .insert(payment_attempt_data)
        .execute()
    )

    if not payment_attempt_response.data:
        raise HTTPException(
            status_code=500,
            detail=(
                "Razorpay order created but payment attempt "
                "could not be recorded."
            ),
        )

    payment_attempt = payment_attempt_response.data[0]

    # -----------------------------------------------------
    # 6. Audit order creation
    # -----------------------------------------------------

    audit_log = create_audit_log(
        transaction_id=transaction_id,
        action="PAYMENT_ORDER_CREATED",
        details={
            "provider": "razorpay",
            "order_id": razorpay_order_id,
            "order_status": razorpay_order.get("status"),
            "amount": amount,
            "currency": currency,
            "transaction_status": transaction_status,
            "source": "razorpay_payment_service",
        },
    )

    # -----------------------------------------------------
    # 7. Return Razorpay checkout information
    # -----------------------------------------------------

    return {
        "success": True,
        "transaction": transaction,
        "payment": {
            "success": True,
            "provider": "razorpay",
            "order_id": razorpay_order_id,
            "status": razorpay_order.get("status"),
            "amount": amount,
            "currency": currency,
            "key_id": RAZORPAY_KEY_ID,
        },
        "payment_attempt": payment_attempt,
        "audit_log": audit_log,
        "message": (
            "Razorpay payment order created successfully."
        ),
    }


# =========================================================
# VERIFY RAZORPAY PAYMENT
# =========================================================

@router.post("/verify")
def verify_payment(
    request: PaymentVerificationRequest,
) -> dict[str, Any]:

    # -----------------------------------------------------
    # 1. Fetch transaction
    # -----------------------------------------------------

    transaction_response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("id", request.transaction_id)
        .limit(1)
        .execute()
    )

    if not transaction_response.data:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    transaction = transaction_response.data[0]

    transaction_id = transaction["id"]
    transaction_status = transaction.get("status")

    # -----------------------------------------------------
    # 2. Handle already verified payment
    # -----------------------------------------------------

    if transaction_status == "paid":
        return {
            "success": True,
            "transaction": transaction,
            "payment": {
                "provider": "razorpay",
                "order_id": request.razorpay_order_id,
                "payment_id": request.razorpay_payment_id,
                "status": "verified",
            },
            "message": "Payment already verified.",
        }

    # -----------------------------------------------------
    # 3. Transaction must be approved
    # -----------------------------------------------------

    if transaction_status != "approved":
        raise HTTPException(
            status_code=400,
            detail=(
                "Payment verification cannot proceed for "
                f"transaction status: {transaction_status}"
            ),
        )

    # -----------------------------------------------------
    # 4. Verify Razorpay signature
    # -----------------------------------------------------

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": request.razorpay_order_id,
                "razorpay_payment_id": request.razorpay_payment_id,
                "razorpay_signature": request.razorpay_signature,
            }
        )

    except Exception as exc:

        # -----------------------------------------------
        # Audit failed verification
        # -----------------------------------------------

        try:
            create_audit_log(
                transaction_id=transaction_id,
                action="PAYMENT_VERIFICATION_FAILED",
                details={
                    "provider": "razorpay",
                    "order_id": request.razorpay_order_id,
                    "payment_id": request.razorpay_payment_id,
                    "reason": "INVALID_SIGNATURE",
                    "error": str(exc),
                    "source": "razorpay_payment_verification",
                },
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=400,
            detail="Razorpay payment signature verification failed.",
        )

    # -----------------------------------------------------
    # 5. Find payment attempt
    # -----------------------------------------------------

    payment_attempt_response = (
        supabase
        .table("payment_attempts")
        .select("*")
        .eq("transaction_id", transaction_id)
        .eq("provider", "razorpay")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    payment_attempt = None

    if payment_attempt_response.data:
        payment_attempt = payment_attempt_response.data[0]

    # -----------------------------------------------------
    # 6. Update payment attempt
    # -----------------------------------------------------

    if payment_attempt:

        payment_attempt_update_response = (
            supabase
            .table("payment_attempts")
            .update(
                {
                    "provider_payment_id":
                        request.razorpay_payment_id,
                    "status": "paid",
                }
            )
            .eq("id", payment_attempt["id"])
            .execute()
        )

        if payment_attempt_update_response.data:
            payment_attempt = (
                payment_attempt_update_response.data[0]
            )

    # -----------------------------------------------------
    # 7. Update transaction to PAID
    # -----------------------------------------------------

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
            detail=(
                "Payment was verified but transaction "
                "status could not be updated."
            ),
        )

    updated_transaction = (
        transaction_update_response.data[0]
    )

    # -----------------------------------------------------
    # 8. Create successful verification audit
    # -----------------------------------------------------

    audit_log = create_audit_log(
        transaction_id=transaction_id,
        action="PAYMENT_VERIFIED",
        details={
            "provider": "razorpay",
            "order_id": request.razorpay_order_id,
            "payment_id": request.razorpay_payment_id,
            "payment_status": "verified",
            "transaction_status": "paid",
            "amount": float(transaction["amount"]),
            "currency": transaction.get(
                "currency",
                "INR",
            ),
            "source": "razorpay_payment_verification",
        },
    )

    # -----------------------------------------------------
    # 9. Return verified payment
    # -----------------------------------------------------

    return {
        "success": True,
        "transaction": updated_transaction,
        "payment": {
            "provider": "razorpay",
            "order_id": request.razorpay_order_id,
            "payment_id": request.razorpay_payment_id,
            "status": "verified",
        },
        "payment_attempt": payment_attempt,
        "audit_log": audit_log,
        "message": (
            "Razorpay payment verified successfully."
        ),
    }