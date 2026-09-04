from typing import Any
from uuid import uuid4


class MockPaymentProvider:
    provider_name = "mock"

    def create_payment(
        self,
        transaction_id: str,
        amount: float,
        currency: str = "INR",
    ) -> dict[str, Any]:
        payment_id = f"mock_pay_{uuid4().hex[:12]}"

        return {
            "success": True,
            "provider": self.provider_name,
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "status": "created",
        }

    def process_payment(
        self,
        payment_id: str,
    ) -> dict[str, Any]:
        return {
            "success": True,
            "provider": self.provider_name,
            "payment_id": payment_id,
            "status": "paid",
        }