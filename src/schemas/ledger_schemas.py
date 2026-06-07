import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import TransactionStatus


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


class TransactionBase(BaseModel):
    id: uuid.UUID
    status: TransactionStatus
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LedgerEntryResponse(BaseModel):
    id: uuid.UUID
    amount: Decimal
    created_at: datetime
    transaction: TransactionBase

    model_config = ConfigDict(from_attributes=True)
