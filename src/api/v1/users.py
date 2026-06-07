from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user
from src.domain.models import User
from src.schemas.user_schemas import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
