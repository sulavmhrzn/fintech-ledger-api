import asyncio
from datetime import datetime, timezone

from redmail import EmailSender
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config.logger import logger
from src.config.settings import settings
from src.domain.models import OTPToken
from src.workers.celery_app import celery_app

mailer = EmailSender(
    host=settings.SMTP_HOST, port=settings.SMTP_PORT, use_starttls=False
)


@celery_app.task(name="send_verification_email_task", bind=True, max_retries=3)
def send_verification_email(self, email: str, code: str) -> str:

    try:
        mailer.send(
            subject="Verify your Fintech Account",
            sender=settings.SENDER_EMAIL,
            receivers=[email],
            text="Welcome! Your 6-digit verification code is: {{ code }}",
            html="""
                <html>
                    <body>
                        <h2>Welcome to Fintech Ledger!</h2>
                        <p>Please use the following 6-digit code to verify your email address:</p>
                        <h1 style="color: #2b6cb0; letter-spacing: 5px;">{{ code }}</h1>
                        <p>This code will expire in 15 minutes.</p>
                    </body>
                </html>
            """,
            body_params={"code": code},
        )

        logger.info(f"Email successfully sent to {email}")
        return f"Success: sent to {email}"

    except Exception as exc:
        logger.error("send_verification_email_failed", email=email, error=str(exc))
        raise self.retry(exc=exc, countdown=2**self.request.retries)


async def _delete_expired_tokens_async():
    local_engine = create_async_engine(settings.DATABASE_URL)
    local_session_maker = async_sessionmaker(local_engine, expire_on_commit=False)

    try:
        async with local_session_maker() as session:
            query = delete(OTPToken).where(
                OTPToken.expires_at < datetime.now(timezone.utc)
            )
            result = await session.execute(query)
            await session.commit()

            logger.info("delete_expired_tokens_success", count=result.rowcount)  # ty:ignore[unresolved-attribute]
    finally:
        await local_engine.dispose()


@celery_app.task(name="cleanup_expired_otp_tokens")
def cleanup_expired_otp_tokens_task():
    asyncio.run(_delete_expired_tokens_async())
