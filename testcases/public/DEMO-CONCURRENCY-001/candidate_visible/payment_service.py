from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Payment:
    payment_id: str
    request_id: str
    amount: Decimal


class PaymentRepository(Protocol):
    def find_by_request_id(self, request_id: str) -> Payment | None: ...

    def next_id(self) -> str: ...

    def save(self, payment: Payment) -> None: ...


class PaymentService:
    def __init__(self, repository: PaymentRepository) -> None:
        self._repository = repository

    def create_payment(self, request_id: str, amount: Decimal) -> Payment:
        existing = self._repository.find_by_request_id(request_id)
        if existing is not None:
            return existing

        payment = Payment(
            payment_id=self._repository.next_id(),
            request_id=request_id,
            amount=amount,
        )
        self._repository.save(payment)
        return payment

