import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class TransferCreate(BaseModel):
    to_wallet_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    transaction_pin: str
    description: str | None = Field(default=None, max_length=255)
    idempotency_key: str = Field(min_length=10, max_length=100)


class DepositCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    description: str | None = Field(default="External mock deposit", max_length=255)
    idempotency_key: str = Field(min_length=10, max_length=100)
