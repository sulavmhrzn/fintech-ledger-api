import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import LedgerEntry, Transaction


async def get_wallet_balance(session: AsyncSession, wallet_id: uuid.UUID) -> Decimal:
    query = select(func.sum(LedgerEntry.amount)).where(
        LedgerEntry.wallet_id == wallet_id
    )
    result = await session.execute(query)
    balance = result.scalar()

    return balance if balance is not None else Decimal("0.00")


async def get_transaction_by_idempotency_key(
    session: AsyncSession, key: str
) -> Transaction | None:
    query = select(Transaction).where(Transaction.idempotency_key == key)
    result = await session.execute(query)
    return result.scalar_one_or_none()
