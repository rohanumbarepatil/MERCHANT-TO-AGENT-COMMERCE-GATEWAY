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

    # Fetch transaction
    transaction_response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("id", request.transaction_id)
        .single()
        .execute()
    )

    transaction = transaction_response.data

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    # Approval is only valid for transactions waiting for approval
    if transaction["status"] != "approval_required":
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction does not require approval. "
                f"Current status: {transaction['status']}"
            ),
        )

    # Create approval record
    approval_response = (
        supabase
        .table("approvals")
        .insert(
            {
                "transaction_id": transaction["id"],
                "status": "approved",
                "approved_by": request.approved_by,
            }
        )
        .execute()
    )

    approval = approval_response.data[0]

    # Update transaction status
    transaction_update_response = (
        supabase
        .table("transactions")
        .update(
            {
                "status": "approved",
            }
        )
        .eq(
            "id",
            transaction["id"],
        )
        .execute()
    )

    updated_transaction = transaction_update_response.data[0]

    # Create audit log
    supabase.table("audit_logs").insert(
        {
            "transaction_id": transaction["id"],
            "action": "TRANSACTION_APPROVED",
            "details": {
                "approved_by": request.approved_by,
                "approval_id": approval["id"],
            },
        }
    ).execute()

    return {
        "success": True,
        "approval": approval,
        "transaction": updated_transaction,
        "message": "Transaction approved successfully.",
    }