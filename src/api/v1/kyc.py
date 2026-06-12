from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.config.database import get_db_session
from src.domain.models import User
from src.schemas.kyc_schemas import KYCDocumentResponse
from src.services.kyc_service import process_kyc_upload

router = APIRouter(prefix="/kyc", tags=["KYC"])


@router.post(
    "/documents",
    response_model=KYCDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a KYC Document",
)
async def upload_document_endpoint(
    document_type: str = Form(..., description="e.g., PASSPORT, CITIZENSHIP, LICENSE"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await process_kyc_upload(
        session=session, user=current_user, document_type=document_type, file=file
    )
