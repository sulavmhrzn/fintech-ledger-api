import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import KYCStatus
from src.domain.models import KYCDocument


async def get_kyc_document_by_id(
    session: AsyncSession, document_id: uuid.UUID
) -> KYCDocument | None:
    query = select(KYCDocument).where(KYCDocument.id == document_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_kyc_documents(
    session: AsyncSession, kyc_status: KYCStatus
) -> list[KYCDocument]:
    query = (
        select(KYCDocument)
        .where(KYCDocument.status == kyc_status)
        .order_by(KYCDocument.created_at.asc())
    )
    result = await session.execute(query)
    return list(result.scalars().all())
