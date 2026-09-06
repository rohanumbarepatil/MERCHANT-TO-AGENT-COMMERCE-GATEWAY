from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.client import supabase
from app.policy.engine.engine import evaluate_purchase


router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"],
)


class TransactionRequest(BaseModel):
    agent_id: str
    merchant_id: str
    product_id: str

@router.get("/{transaction_id}")
def get_transaction(transaction_id: str) -> dict[str, Any]:
    response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("id", transaction_id)
        .single()
        .execute()
    )

    transaction = response.data

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return {
        "success": True,
        "transaction": transaction,
    }

@router.post("/")
def create_transaction(
    request: TransactionRequest,
) -> dict[str, Any]:

    # Fetch product
    product_response = (
        supabase
        .table("products")
        .select("*")
        .eq("id", request.product_id)
        .single()
        .execute()
    )

    product = product_response.data

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # Fetch merchant
    merchant_response = (
        supabase
        .table("merchants")
        .select("*")
        .eq("id", request.merchant_id)
        .single()
        .execute()
    )

    merchant = merchant_response.data

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found",
        )

    # Fetch agent
    agent_response = (
        supabase
        .table("agents")
        .select("*")
        .eq("id", request.agent_id)
        .single()
        .execute()
    )

    agent = agent_response.data

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    amount = float(product["price"])

    # Select policy based on transaction amount
    if amount > 5000:
        policy_name = "High Value Purchase Policy"
    else:
        policy_name = "Standard Purchase Policy"

    policy_response = (
        supabase
        .table("policies")
        .select("*")
        .eq("name", policy_name)
        .single()
        .execute()
    )

    policy = policy_response.data

    if not policy:
        raise HTTPException(
            status_code=404,
            detail=f"{policy_name} not found",
        )

    # Evaluate transaction against policy
    decision = evaluate_purchase(
        amount=amount,
        policy=policy,
    )

    # Map policy decision to transaction status
    status_map = {
        "APPROVED": "approved",
        "APPROVAL_REQUIRED": "approval_required",
        "BLOCKED": "blocked",
    }

    transaction_status = status_map.get(
        decision["decision"],
        "blocked",
    )

    # Create transaction
    transaction_response = (
        supabase
        .table("transactions")
        .insert(
            {
                "agent_id": request.agent_id,
                "merchant_id": request.merchant_id,
                "product_id": request.product_id,
                "amount": amount,
                "currency": product.get("currency", "INR"),
                "status": transaction_status,
            }
        )
        .execute()
    )

    transaction = transaction_response.data[0]

    # Create audit log
    supabase.table("audit_logs").insert(
        {
            "transaction_id": transaction["id"],
            "action": "POLICY_EVALUATED",
            "details": {
                "decision": decision["decision"],
                "reason": decision["reason"],
                "policy": policy["name"],
                "amount": amount,
            },
        }
    ).execute()

    return {
        "success": True,
        "transaction": transaction,
        "decision": decision,
        "policy": {
            "name": policy["name"],
            "requires_approval": policy["requires_approval"],
        },
        "product": {
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
        },
        "agent": {
            "id": agent["id"],
            "name": agent["name"],
        },
        "merchant": {
            "id": merchant["id"],
            "name": merchant["name"],
        },
    }