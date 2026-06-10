import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import Role
from src.domain.models import User


async def get_all_users(session: AsyncSession) -> list[User]:
    query = select(User).order_by(User.created_at.desc())
    result = await session.execute(query)
    return list(result.scalars().all())


async def toggle_user_active_status(
    session: AsyncSession, target_user_id: uuid.UUID
) -> User:
    query = select(User).where(User.id == target_user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.role == Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate another administrator",
        )

    user.is_active = not user.is_active
    await session.commit()
    await session.refresh(user)
    return user
