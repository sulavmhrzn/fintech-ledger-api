import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import Currency
from src.domain.models import Wallet


async def get_wallet_by_user_and_currency(
    session: AsyncSession, user_id: uuid.UUID, currency: Currency
) -> Wallet | None:
    query = select(Wallet).where(Wallet.user_id == user_id, Wallet.currency == currency)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_wallets(session: AsyncSession, user_id: uuid.UUID) -> list[Wallet]:
    query = select(Wallet).where(Wallet.user_id == user_id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_wallet_by_id(
    session: AsyncSession, wallet_id: uuid.UUID, lock: bool = False
) -> Wallet | None:
    query = select(Wallet).where(Wallet.id == wallet_id)
    if lock:
        query = query.with_for_update()
    result = await session.execute(query)
    return result.scalar_one_or_none()
