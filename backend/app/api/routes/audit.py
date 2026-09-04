from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.client import supabase


router = APIRouter(
    prefix="/api/approvals",
    tags=["Approvals"],
)


class ApprovalRequest(BaseModel):
    transaction_id: str
    approved_by: str


@router.post("/")
def approve_transaction(
    request: ApprovalRequest,
) -> dict[str, Any]:

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

    # ---------------------------------------------------------
    # 2. Verify approval is actually required
    # ---------------------------------------------------------
    if transaction_status != "approval_required":
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction does not require approval. "
                f"Current status: {transaction_status}"
            ),
        )

    # ---------------------------------------------------------
    # 3. Check for existing approval
    # ---------------------------------------------------------
    existing_approval_response = (
        supabase
        .table("approvals")
        .select("*")
        .eq("transaction_id", transaction_id)
        .limit(1)
        .execute()
    )

    if existing_approval_response.data:
        raise HTTPException(
            status_code=400,
            detail="An approval record already exists for this transaction.",
        )

    # ---------------------------------------------------------
    # 4. Create approval record
    # ---------------------------------------------------------
    approval_response = (
        supabase
        .table("approvals")
        .insert(
            {
                "transaction_id": transaction_id,
                "status": "approved",
                "approved_by": request.approved_by,
            }
        )
        .execute()
    )

    if not approval_response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create approval record.",
        )

    approval = approval_response.data[0]

    # ---------------------------------------------------------
    # 5. Update transaction status
    # ---------------------------------------------------------
    transaction_update_response = (
        supabase
        .table("transactions")
        .update(
            {
                "status": "approved",
            }
        )
        .eq("id", transaction_id)
        .execute()
    )

    if not transaction_update_response.data:
        raise HTTPException(
            status_code=500,
            detail="Approval created but transaction update failed.",
        )

    updated_transaction = transaction_update_response.data[0]

    # ---------------------------------------------------------
    # 6. Create audit log
    # ---------------------------------------------------------
    audit_response = (
        supabase
        .table("audit_logs")
        .insert(
            {
                "transaction_id": transaction_id,
                "action": "TRANSACTION_APPROVED",
                "details": {
                    "approved_by": request.approved_by,
                    "approval_id": approval["id"],
                    "previous_status": "approval_required",
                    "new_status": "approved",
                },
            }
        )
        .execute()
    )

    if not audit_response.data:
        raise HTTPException(
            status_code=500,
            detail="Approval succeeded but audit log creation failed.",
        )

    audit_log = audit_response.data[0]

    # ---------------------------------------------------------
    # 7. Return complete result
    # ---------------------------------------------------------
    return {
        "success": True,
        "approval": approval,
        "transaction": updated_transaction,
        "audit_log": audit_log,
        "message": "Transaction approved successfully.",
    }