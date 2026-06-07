import uuid
from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.security import (
    create_access_token,
    create_refresh_token,
    get_hash,
    verify_hash,
)
from src.config.settings import settings
from src.domain.models import User
from src.schemas.user_schemas import TokenResponse, UserCreate
from src.selectors.user_selectors import get_user_by_email, get_user_by_id


async def register_user(session: AsyncSession, user_data: UserCreate) -> User:
    existing_user = await get_user_by_email(session, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    hashed_pw = get_hash(user_data.password)
    hashed_pin = get_hash(user_data.transaction_pin)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        transaction_pin_hash=hashed_pin,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def authenticate_user(
    session: AsyncSession, form_data: OAuth2PasswordRequestForm
) -> TokenResponse:
    user = await get_user_by_email(session, email=form_data.username)

    if not user or not verify_hash(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )

    token_payload = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


def _get_blacklist_key(jti: str) -> str:
    return f"blacklist:refresh:{jti}"


async def refresh_access_token(
    session: AsyncSession, refresh_token: str, redis_client: Redis
) -> TokenResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected a refresh token",
            )

        user_id_str = payload.get("sub")
        jti = payload.get("jti")
        exp_timestamp = payload.get("exp")

        if not user_id_str or not jti or not exp_timestamp:
            raise credentials_exception

    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        ValueError,
        ValidationError,
    ):
        raise credentials_exception

    # Redis blacklist check
    blacklist_key = _get_blacklist_key(jti)

    is_blacklisted = await redis_client.get(blacklist_key)
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please login again.",
        )

    user_id = uuid.UUID(user_id_str)
    user = await get_user_by_id(session, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive or deleted",
        )

    # Blacklist old token
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    time_to_live = exp_timestamp - current_timestamp
    if time_to_live > 0:
        await redis_client.setex(
            name=blacklist_key,
            time=time_to_live,
            value="revoked",
        )

    token_payload = {"sub": str(user.id), "role": user.role.value}

    return TokenResponse(
        access_token=create_access_token(token_payload),
        refresh_token=create_refresh_token(token_payload),
        token_type="bearer",
    )
