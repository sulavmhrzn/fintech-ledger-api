import redis.asyncio as Redis
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db_session
from src.config.redis import get_redis
from src.schemas.user_schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from src.services.auth_service import (
    authenticate_user,
    refresh_access_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user profile",
)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session),
):
    new_user = await register_user(session, user_data)
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login to receive an access token",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
):
    return await authenticate_user(session, form_data=form_data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtain a new access token pair using a refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
    redis_client: Redis = Depends(get_redis),
):
    return await refresh_access_token(
        session=session, refresh_token=request.refresh_token, redis_client=redis_client
    )
