import re
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.client import supabase
from app.policy.engine.engine import evaluate_purchase


router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"],
)


class AgentChatRequest(BaseModel):
    message: str
    agent_id: str = "fb35e039-653c-4b38-8ced-448504aec875"


def extract_price(message: str) -> float | None:
    patterns = [
        r"(?:under|below|less than|upto|up to|within)\s*[₹rs.]?\s*([\d,]+)",
        r"[₹rs.]\s*([\d,]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, message.lower())

        if match:
            return float(match.group(1).replace(",", ""))

    return None

def extract_product_query(message: str) -> str:
    text = message.lower()

    keywords = [
        "mechanical keyboard",
        "smart watch",
        "headphones",
        "headphone",
        "keyboard",
        "laptop",
        "watch",
    ]

    for keyword in keywords:
        if keyword in text:
            return keyword

    return text.strip()

def detect_intent(message: str) -> str:
    text = message.lower()

    buy_words = [
        "buy",
        "purchase",
        "order",
        "get me",
    ]

    for word in buy_words:
        if word in text:
            return "purchase"

    return "product_search"


@router.post("/chat")
def agent_chat(
    request: AgentChatRequest,
) -> dict[str, Any]:

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # ---------------------------------------------------------
    # 1. Understand user request
    # ---------------------------------------------------------
    intent = detect_intent(message)
    product_query = extract_product_query(message)
    max_price = extract_price(message)

    # ---------------------------------------------------------
    # 2. Search products
    # ---------------------------------------------------------
    query = (
        supabase
        .table("products")
        .select("*")
        .ilike("name", f"%{product_query}%")
    )

    if max_price is not None:
        query = query.lte("price", max_price)

    response = query.order("price").execute()

    products = response.data

    # ---------------------------------------------------------
    # 3. No products found
    # ---------------------------------------------------------
    if not products:
        return {
            "success": True,
            "intent": intent,
            "query": product_query,
            "max_price": max_price,
            "count": 0,
            "products": [],
            "response": (
                f"I couldn't find a {product_query}"
                + (
                    f" under ₹{max_price:.0f}."
                    if max_price
                    else "."
                )
            ),
        }

    # ---------------------------------------------------------
    # 4. Select best product
    # ---------------------------------------------------------
    selected_product = products[0]

    # ---------------------------------------------------------
    # 5. SEARCH intent
    # ---------------------------------------------------------
    if intent == "product_search":
        return {
            "success": True,
            "intent": "product_search",
            "query": product_query,
            "max_price": max_price,
            "count": len(products),
            "products": products,
            "selected_product": selected_product,
            "response": (
                f"I found {selected_product['name']} "
                f"for ₹{float(selected_product['price']):.0f}."
            ),
        }

    # ---------------------------------------------------------
    # 6. PURCHASE intent
    # ---------------------------------------------------------
    product_id = selected_product["id"]
    merchant_id = selected_product["merchant_id"]
    amount = float(selected_product["price"])

    # Fetch agent
    agent_response = (
        supabase
        .table("agents")
        .select("*")
        .eq("id", request.agent_id)
        .limit(1)
        .execute()
    )

    if not agent_response.data:
        raise HTTPException(
            status_code=404,
            detail="Agent not found.",
        )

    # Select policy
    if amount > 5000:
        policy_name = "High Value Purchase Policy"
    else:
        policy_name = "Standard Purchase Policy"

    policy_response = (
        supabase
        .table("policies")
        .select("*")
        .eq("name", policy_name)
        .limit(1)
        .execute()
    )

    if not policy_response.data:
        raise HTTPException(
            status_code=404,
            detail=f"{policy_name} not found.",
        )

    policy = policy_response.data[0]

    # ---------------------------------------------------------
    # 7. Policy Engine — final authorization decision
    # ---------------------------------------------------------
    decision = evaluate_purchase(
        amount=amount,
        policy=policy,
    )

    status_map = {
        "APPROVED": "approved",
        "APPROVAL_REQUIRED": "approval_required",
        "BLOCKED": "blocked",
    }

    transaction_status = status_map.get(
        decision["decision"],
        "blocked",
    )

    # ---------------------------------------------------------
    # 8. Create transaction
    # ---------------------------------------------------------
    transaction_response = (
        supabase
        .table("transactions")
        .insert(
            {
                "agent_id": request.agent_id,
                "merchant_id": merchant_id,
                "product_id": product_id,
                "amount": amount,
                "currency": selected_product.get(
                    "currency",
                    "INR",
                ),
                "status": transaction_status,
            }
        )
        .execute()
    )

    if not transaction_response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create transaction.",
        )

    transaction = transaction_response.data[0]

    # ---------------------------------------------------------
    # 9. Audit agent decision
    # ---------------------------------------------------------
    audit_response = (
        supabase
        .table("audit_logs")
        .insert(
            {
                "transaction_id": transaction["id"],
                "action": "AGENT_PURCHASE_REQUEST",
                "details": {
                    "message": message,
                    "intent": intent,
                    "product_query": product_query,
                    "product_id": product_id,
                    "amount": amount,
                    "policy": policy_name,
                    "decision": decision["decision"],
                    "source": "agent",
                },
            }
        )
        .execute()
    )

    if not audit_response.data:
        raise HTTPException(
            status_code=500,
            detail="Transaction created but audit log failed.",
        )

    # ---------------------------------------------------------
    # 10. Return result
    # ---------------------------------------------------------
    return {
        "success": True,
        "intent": "purchase",
        "query": product_query,
        "max_price": max_price,
        "selected_product": selected_product,
        "transaction": transaction,
        "policy": {
            "name": policy["name"],
            "requires_approval": policy["requires_approval"],
        },
        "decision": decision,
        "message": (
            "Purchase approved and ready for payment."
            if decision["decision"] == "APPROVED"
            else "Purchase requires user approval."
            if decision["decision"] == "APPROVAL_REQUIRED"
            else "Purchase blocked by policy."
        ),
    }