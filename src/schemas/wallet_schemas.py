import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.domain.enums import Currency


class WalletCreate(BaseModel):
    currency: Currency


class WalletResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    currency: Currency
    is_frozen: bool
    created_at: datetime
    balance: Decimal = Decimal("0.00")

    model_config = ConfigDict(from_attributes=True)
