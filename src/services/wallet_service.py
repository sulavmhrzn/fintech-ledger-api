import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Wallet
from src.schemas.wallet_schemas import WalletCreate
from src.selectors.wallet_selectors import get_wallet_by_user_and_currency


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
