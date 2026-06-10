import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import RequirePermission, RequireRole
from src.config.database import get_db_session
from src.domain.enums import Permission, Role
from src.domain.models import User
from src.schemas.user_schemas import UserResponse
from src.schemas.wallet_schemas import WalletResponse
from src.services.user_service import get_all_users, toggle_user_active_status
from src.services.wallet_service import toggle_wallet_freeze

router = APIRouter(prefix="/admin", tags=["Admin & Compliance"])


@router.post(
    "/wallets/{wallet_id}/toggle-freeze",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
    summary="Freeze or unfreeze a wallet (Compliance Only)",
)
async def freeze_wallet_endpoint(
    wallet_id: uuid.UUID,
    current_user: User = Depends(RequirePermission(Permission.WALLETS_FREEZE)),
    session: AsyncSession = Depends(get_db_session),
):
    return await toggle_wallet_freeze(session, wallet_id)


@router.get(
    "/users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users (Admin & Compliance)",
)
async def list_all_users_endpoint(
    current_user: User = Depends(RequirePermission(Permission.USERS_READ)),
    session: AsyncSession = Depends(get_db_session),
):
    return await get_all_users(session)


@router.post(
    "/users/{target_user_id}/toggle-active",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Ban or Un-ban a user (Admin Only)",
)
async def toggle_user_access_endpoint(
    target_user_id: uuid.UUID,
    current_user: User = Depends(RequirePermission(Permission.USERS_BAN)),
    session: AsyncSession = Depends(get_db_session),
):
    return await toggle_user_active_status(session, target_user_id)
