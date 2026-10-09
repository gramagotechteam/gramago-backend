from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User



from app.services.delivery_push_notification_service import (
    DeliveryPushNotificationService,
)


class DeliveryAuthService:

    @staticmethod
    async def get_delivery_user(
        db: AsyncSession,
        identifier: str,
    ) -> User | None:

        identifier = identifier.strip()

        result = await db.execute(
            select(User)
            .options(
                selectinload(User.delivery_profile)
            )
            .where(
                or_(
                    User.email == identifier.lower(),
                    User.phone == identifier,
                )
            )
        )

        return result.scalar_one_or_none()


    @staticmethod
    def validate_delivery_access(
        user: User,
    ) -> None:

        if user.role != "DELIVERY_PARTNER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account is not a delivery partner account.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your delivery account is inactive.",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not verified.",
            )

        profile = user.delivery_profile

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Delivery partner profile not found.",
            )

        if not profile.is_approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your delivery account is awaiting admin approval.",
            )