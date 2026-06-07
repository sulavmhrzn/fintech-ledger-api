import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.domain.enums import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        description="Password must be at least 8 characters long",
    )
    transaction_pin: str = Field(
        min_length=4,
        max_length=6,
        pattern=r"^\d+$",
        description="Must be a 4 to 6 digit numeric PIN.",
    )


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: Role
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str
