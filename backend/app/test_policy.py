from app.policy.engine.engine import evaluate_purchase


policy = {
    "max_amount": 5000,
    "requires_approval": False,
}


tests = [
    2999,
    5000,
    7000,
]


for amount in tests:
    result = evaluate_purchase(amount, policy)

    print(f"₹{amount} -> {result['decision']}")
    print(result["message"])
    print("---")