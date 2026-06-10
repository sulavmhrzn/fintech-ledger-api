import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Wallet
from src.schemas.wallet_schemas import WalletCreate
from src.selectors.wallet_selectors import (
    get_wallet_by_id,
    get_wallet_by_user_and_currency,
)


async def create_wallet(
    session: AsyncSession, user_id: uuid.UUID, wallet_data: WalletCreate
) -> Wallet:
    existing_wallet = await get_wallet_by_user_and_currency(
        session, user_id=user_id, currency=wallet_data.currency
    )

    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You already have a {wallet_data.currency.value} wallet.",
        )

    new_wallet = Wallet(user_id=user_id, currency=wallet_data.currency)
    session.add(new_wallet)
    await session.commit()
    await session.refresh(new_wallet)
    return new_wallet


async def toggle_wallet_freeze(session: AsyncSession, wallet_id: uuid.UUID) -> Wallet:
    wallet = get_wallet_by_id(session, wallet_id)

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    wallet.is_frozen = not wallet.is_frozen

    await session.commit()
    await session.refresh(wallet)
    return wallet
