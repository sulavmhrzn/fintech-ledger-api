import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.models import LedgerEntry, Transaction, Wallet


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


async def get_wallet_transactions(
    session: AsyncSession, wallet_id: uuid.UUID
) -> list[LedgerEntry]:
    query = (
        select(LedgerEntry)
        .options(joinedload(LedgerEntry.transaction))
        .where(LedgerEntry.wallet_id == wallet_id)
        .order_by(LedgerEntry.created_at.desc())
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_daily_transfer_volume(
    session: AsyncSession, user_id: uuid.UUID
) -> Decimal:
    twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(days=1)

    query = (
        select(func.sum(LedgerEntry.amount))
        .join(Wallet, Wallet.id == LedgerEntry.wallet_id)
        .where(Wallet.user_id == user_id)
        .where(LedgerEntry.amount < 0)
        .where(LedgerEntry.created_at >= twenty_four_hours_ago)
    )

    result = await session.execute(query)
    total_negative_volume = result.scalar()

    if total_negative_volume is None:
        return Decimal("0.00")
    return abs(total_negative_volume)
