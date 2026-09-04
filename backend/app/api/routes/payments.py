from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.client import supabase


router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"],
)


class PaymentRequest(BaseModel):
    transaction_id: str


def create_mock_payment(amount: float, currency: str = "INR") -> dict[str, Any]:
    """
    Mock payment provider used for development/demo.
    No real money is processed.
    """
    import uuid

    payment_id = f"mock_pay_{uuid.uuid4().hex[:10]}"

    return {
        "success": True,
        "provider": "mock",
        "payment_id": payment_id,
        "status": "paid",
        "amount": amount,
        "currency": currency,
    }


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
            detail="Payment succeeded but audit log creation failed.",
        )

    return response.data[0]


@router.post("/")
def process_payment(request: PaymentRequest):
    # ---------------------------------------------------------
    # 1. Fetch transaction
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. Prevent duplicate payment
    # ---------------------------------------------------------
    if transaction_status == "paid":
        raise HTTPException(
            status_code=400,
            detail="Payment cannot be processed for transaction status: paid",
        )

    # ---------------------------------------------------------
    # 3. Only approved transactions can be paid
    # ---------------------------------------------------------
    if transaction_status != "approved":
        raise HTTPException(
            status_code=400,
            detail=(
                "Payment cannot be processed for transaction status: "
                f"{transaction_status}"
            ),
        )

    # ---------------------------------------------------------
    # 4. Create mock payment
    # ---------------------------------------------------------
    payment = create_mock_payment(
        amount=amount,
        currency=currency,
    )

    if not payment["success"]:
        raise HTTPException(
            status_code=400,
            detail="Payment failed.",
        )

    payment_id = payment["payment_id"]

    # ---------------------------------------------------------
    # 5. Create payment attempt
    # ---------------------------------------------------------
    payment_attempt_data = {
        "transaction_id": transaction_id,
        "provider": payment["provider"],
        "provider_payment_id": payment_id,
        "status": payment["status"],
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
            detail="Payment succeeded but payment attempt could not be recorded.",
        )

    payment_attempt = payment_attempt_response.data[0]

    # ---------------------------------------------------------
    # 6. Update transaction status
    # ---------------------------------------------------------
    transaction_update_response = (
        supabase
        .table("transactions")
        .update({"status": "paid"})
        .eq("id", transaction_id)
        .execute()
    )

    if not transaction_update_response.data:
        raise HTTPException(
            status_code=500,
            detail="Payment succeeded but transaction status update failed.",
        )

    updated_transaction = transaction_update_response.data[0]

    # ---------------------------------------------------------
    # 7. Automatically create audit log
    # ---------------------------------------------------------
    audit_log = create_audit_log(
        transaction_id=transaction_id,
        action="PAYMENT_COMPLETED",
        details={
            "provider": payment["provider"],
            "payment_id": payment_id,
            "payment_status": payment["status"],
            "amount": amount,
            "currency": currency,
            "transaction_status": "paid",
            "source": "payment_service",
        },
    )

    # ---------------------------------------------------------
    # 8. Return complete payment result
    # ---------------------------------------------------------
    return {
        "success": True,
        "transaction": updated_transaction,
        "payment": {
            "success": True,
            "provider": payment["provider"],
            "payment_id": payment_id,
            "status": payment["status"],
            "amount": amount,
            "currency": currency,
        },
        "payment_attempt": payment_attempt,
        "audit_log": audit_log,
        "message": "Payment completed successfully.",
    }