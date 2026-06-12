import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.domain.enums import KYCStatus


class KYCDocumentResponse(BaseModel):
    id: uuid.UUID
    users_id: uuid.UUID
    document_type: str
    status: KYCStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KYCReviewRequest(BaseModel):
    status: KYCStatus
    rejection_reason: str | None = None
