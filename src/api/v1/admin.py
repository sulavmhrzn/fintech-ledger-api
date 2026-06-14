import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import RequirePermission
from src.config.database import get_db_session
from src.domain.enums import KYCStatus, Permission
from src.domain.models import User
from src.schemas.kyc_schemas import KYCDocumentResponse, KYCReviewRequest
from src.schemas.pagination_schema import CursorPage
from src.schemas.user_schemas import UserResponse
from src.schemas.wallet_schemas import WalletResponse
from src.selectors.kyc_selectors import get_kyc_documents
from src.services.kyc_service import review_kyc_document
from src.services.storage_service import create_presigned_url
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


@router.post(
    "/kyc/{document_id}/review",
    response_model=KYCDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve or Reject a KYC Document",
)
async def review_kyc_endpoint(
    document_id: uuid.UUID,
    review_data: KYCReviewRequest,
    current_user: User = Depends(RequirePermission(Permission.KYC_REVIEW)),
    session: AsyncSession = Depends(get_db_session),
):
    return await review_kyc_document(
        session=session,
        document_id=document_id,
        reviewer_id=current_user.id,
        review_data=review_data,
    )


@router.get(
    "/kyc",
    response_model=CursorPage[KYCDocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List KYC Documents",
)
async def list_kyc_endpoint(
    status: KYCStatus = Query(KYCStatus.PENDING),
    limit: int = Query(10, ge=1, le=100),
    cursor: str | None = Query(None),
    current_user: User = Depends(RequirePermission(Permission.KYC_READ)),
    session: AsyncSession = Depends(get_db_session),
):
    documents, next_cursor = await get_kyc_documents(
        session=session,
        kyc_status=status,
        limit=limit,
        cursor=cursor,
    )
    for doc in documents:
        doc.file_url = create_presigned_url(doc.file_url)
    return CursorPage(
        items=documents,
        next_cursor=next_cursor,
    )
