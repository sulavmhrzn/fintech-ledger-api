import uuid

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import KYCStatus
from src.domain.models import KYCDocument
from src.utils.pagination import decode_cursor, encode_cursor


async def get_kyc_document_by_id(
    session: AsyncSession, document_id: uuid.UUID
) -> KYCDocument | None:
    query = select(KYCDocument).where(KYCDocument.id == document_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_kyc_documents(
    session: AsyncSession,
    kyc_status: KYCStatus,
    limit: int = 10,
    cursor: str | None = None,
) -> tuple[list[KYCDocument], str | None]:
    query = select(KYCDocument).where(KYCDocument.status == kyc_status)
    if cursor:
        cursor_dt, cursor_id = decode_cursor(cursor)

        query = query.where(
            tuple_(KYCDocument.created_at, KYCDocument.id)
            > tuple_(cursor_dt, cursor_id)  # ty:ignore[invalid-argument-type]
        )
    query = query.order_by(KYCDocument.created_at.asc(), KYCDocument.id.asc()).limit(
        limit + 1
    )
    result = await session.execute(query)
    documents = list(result.scalars().all())

    next_cursor = None

    if len(documents) > limit:
        documents.pop()
        last_doc = documents[-1]
        next_cursor = encode_cursor(last_doc.created_at, last_doc.id)
    return documents, next_cursor
