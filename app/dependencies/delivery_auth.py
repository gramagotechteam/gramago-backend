from fastapi import (
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User


async def get_current_delivery_partner(
    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
) -> User:

    result = await db.execute(
        select(User)
        .options(
            selectinload(
                User.delivery_profile
            )
        )
        .where(
            User.id == current_user.id
        )
    )

    user = result.scalar_one_or_none()
    # print("11111111111111111111111")
    
    # print("user===",result)
    
    # print("22222222222222222222222")

    if user is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication required",
        )

    # =========================================================
    # DELIVERY ROLE
    # =========================================================

    if user.role != "DELIVERY_PARTNER":
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Delivery partner access required"
            ),
        )

    # =========================================================
    # ACTIVE
    # =========================================================

    if not user.is_active:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Delivery account is disabled"
            ),
        )

    # =========================================================
    # VERIFIED
    # =========================================================

    if not user.is_verified:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Delivery account is not verified"
            ),
        )

    # =========================================================
    # PROFILE
    # =========================================================

    profile = user.delivery_profile

    if profile is None:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Delivery partner profile not found"
            ),
        )

    # =========================================================
    # APPROVAL
    # =========================================================

    if not profile.is_approved:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Delivery account is not approved"
            ),
        )

    return user


