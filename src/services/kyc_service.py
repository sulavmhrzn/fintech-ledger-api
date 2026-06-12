import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import AccountTier, KYCStatus
from src.domain.models import KYCDocument, User
from src.schemas.kyc_schemas import KYCReviewRequest
from src.selectors.kyc_selectors import get_kyc_document_by_id
from src.services.storage_service import upload_file_to_s3


async def process_kyc_upload(
    session: AsyncSession, user: User, document_type: str, file: UploadFile
) -> KYCDocument:
    file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
    s3_key = f"{user.id}/{uuid.uuid4()}.{file_extension}"

    file_url = upload_file_to_s3(
        file_obj=file.file,
        destination_path=s3_key,
        content_type=file.content_type or "application/octet-stream",
    )

    new_document = KYCDocument(
        users_id=user.id,
        document_type=document_type,
        file_url=file_url,
    )

    session.add(new_document)
    await session.commit()
    await session.refresh(new_document)
    return new_document


async def review_kyc_document(
    session: AsyncSession,
    document_id: uuid.UUID,
    reviewer_id: uuid.UUID,
    review_data: KYCReviewRequest,
) -> KYCDocument:
    document = await get_kyc_document_by_id(session, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="KYC document not found"
        )

    if document.status != KYCStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has already been reviewed.",
        )

    document.status = review_data.status
    document.rejection_reason = review_data.rejection_reason
    document.reviewed_by_id = reviewer_id

    if review_data.status == KYCStatus.APPROVED:
        user_query = select(User).where(User.id == document.users_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one()

        if user.tier == AccountTier.TIER_1:
            user.tier = AccountTier.TIER_2
    await session.commit()
    await session.refresh(document)

    return document
