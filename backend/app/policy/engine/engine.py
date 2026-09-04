from typing import Any


def evaluate_purchase(
    amount: float,
    policy: dict[str, Any],
    category: str | None = None,
) -> dict[str, Any]:
    max_amount = float(policy.get("max_amount", 0))
    requires_approval = bool(policy.get("requires_approval", False))

    if amount <= 0:
        return {
            "decision": "BLOCKED",
            "reason": "INVALID_AMOUNT",
            "message": "Purchase amount must be greater than zero.",
        }

    if amount > max_amount:
        return {
            "decision": "BLOCKED",
            "reason": "POLICY_LIMIT",
            "message": f"Transaction exceeds the authorized limit of ₹{max_amount:.2f}.",
            "amount": amount,
            "max_amount": max_amount,
        }

    if requires_approval:
        return {
            "decision": "APPROVAL_REQUIRED",
            "reason": "POLICY_REQUIRES_APPROVAL",
            "message": "Purchase requires user approval.",
            "amount": amount,
            "max_amount": max_amount,
        }

    return {
        "decision": "APPROVED",
        "reason": "WITHIN_POLICY",
        "message": "Purchase is within the authorized policy.",
        "amount": amount,
        "max_amount": max_amount,
    }