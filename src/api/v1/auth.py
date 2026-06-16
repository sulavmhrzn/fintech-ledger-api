from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio.client import Redis
from redis.commands.search.querystring import tags
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db_session
from src.config.redis import get_redis
from src.domain.enums import OTPPurpose
from src.schemas.user_schemas import (
    RefreshTokenRequest,
    ResendVerificationEmailRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    VerifyEmailRequest,
)
from src.selectors.user_selectors import get_user_by_email
from src.services import otp_service
from src.services.auth_service import (
    authenticate_user,
    refresh_access_token,
    register_user,
)
from src.services.otp_service import generate_otp, invalidate_old_tokens, verify_otp
from src.workers.tasks import send_verification_email

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


@router.post("/verify-email", response_model=UserResponse, tags=["Authentication"])
async def verify_email(
    request: VerifyEmailRequest, session: AsyncSession = Depends(get_db_session)
):
    user = await get_user_by_email(session, email=request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.email_verified:
        return user

    await verify_otp(
        session=session,
        user=user,
        code=request.code,
        purpose=OTPPurpose.EMAIL_VERIFICATION,
    )

    user.email_verified = True
    await session.commit()

    return user


@router.post(
    "/resend-verification", status_code=status.HTTP_200_OK, tags=["Authentication"]
)
async def resend_verification(
    request: ResendVerificationEmailRequest,
    session: AsyncSession = Depends(get_db_session),
):
    user = await get_user_by_email(session, email=request.email)
    if not user:
        return {"message": "If that email is registered, a new code has been sent."}

    if user.email_verified:
        return {"message": "Email is already verified"}

    await invalidate_old_tokens(
        session, user_id=user.id, purpose=OTPPurpose.EMAIL_VERIFICATION
    )
    new_otp = await generate_otp(
        session, user_id=user.id, purpose=OTPPurpose.EMAIL_VERIFICATION
    )

    send_verification_email.delay(email=user.email, code=new_otp.code)

    return {"message": "If that email is registered, a new code has been sent."}
