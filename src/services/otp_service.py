import secrets
import string
from datetime import datetime, timedelta, timezone
from email import message
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logger import logger
from src.config.settings import settings
from src.domain.enums import OTPPurpose
from src.domain.models import OTPToken, User
from src.schemas.user_schemas import VerifyEmailRequest
from src.selectors.user_selectors import get_user_by_email


async def generate_otp(
    session: AsyncSession, user_id: UUID, purpose: OTPPurpose
) -> OTPToken:
    code = "".join(secrets.choice(string.digits) for _ in range(6))

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.OTP_EXPIRATION_MINUTES
    )

    otp_token = OTPToken(
        user_id=user_id,
        code=code,
        expires_at=expires_at,
        is_used=False,
        purpose=purpose,
    )

    session.add(otp_token)
    await session.commit()
    await session.refresh(otp_token)
    logger.info("otp_generated_successfully", user_id=str(user_id), purpose=purpose)

    return otp_token


async def verify_otp(
    session: AsyncSession, user: User, code: str, purpose: OTPPurpose
) -> User | None:

    query = (
        select(OTPToken)
        .where(
            OTPToken.user_id == user.id,
            OTPToken.code == code,
            OTPToken.purpose == purpose,
            OTPToken.is_used == False,
        )
        .order_by(OTPToken.created_at.desc())
    )

    result = await session.execute(query)
    otp_token = result.scalars().first()

    if not otp_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {purpose.value} code.",
        )

    if otp_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="OTP code has expired"
        )

    otp_token.is_used = True
    await session.commit()
    await session.refresh(user)
    logger.info("verify_otp_success", email=user.email, purpose=purpose)
    return user


async def invalidate_old_tokens(
    session: AsyncSession, user_id: UUID, purpose: OTPPurpose
):
    query = (
        update(OTPToken)
        .where(
            OTPToken.user_id == user_id,
            OTPToken.purpose == purpose,
            OTPToken.is_used == False,
        )
        .values(is_used=True)
    )

    await session.execute(query)
    await session.commit()
