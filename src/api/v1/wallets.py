from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.config.database import get_db_session
from src.domain.models import User
from src.schemas.wallet_schemas import WalletCreate, WalletResponse
from src.selectors.ledger_selectors import get_wallet_balance
from src.selectors.wallet_selectors import get_user_wallets
from src.services.wallet_service import create_wallet

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.post(
    "",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Open a new wallet",
)
async def open_wallet(
    wallet_data: WalletCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    new_wallet = await create_wallet(
        session=session, user_id=current_user.id, wallet_data=wallet_data
    )
    return new_wallet


@router.get(
    "",
    response_model=list[WalletResponse],
    status_code=status.HTTP_200_OK,
    summary="List all my wallets",
)
async def get_my_wallets(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    wallets = await get_user_wallets(session=session, user_id=current_user.id)

    response_list = []

    for wallet in wallets:
        balance = await get_wallet_balance(session, wallet.id)

        wallet_data = {
            "id": wallet.id,
            "user_id": wallet.user_id,
            "currency": wallet.currency,
            "is_frozen": wallet.is_frozen,
            "created_at": wallet.created_at,
            "balance": balance,
        }
        response_list.append(wallet_data)
    return response_list
