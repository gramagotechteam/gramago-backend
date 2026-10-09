from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.services.delivery_assignment_service import (
    DeliveryAssignmentService,
)


from app.models.user import User
from sqlalchemy import select

from app.models.delivery_assignment import (
    DeliveryAssignment,
)

class DeliveryStatusService:

    # =========================================================
    # GET PROFILE
    # =========================================================

    @staticmethod
    def get_profile(
        user: User,
    ):
        profile = user.delivery_profile

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery partner profile not found",
            )

        return profile


    # =========================================================
    # ONLINE / OFFLINE
    # =========================================================

    @staticmethod
    async def set_online_status(
        db: AsyncSession,
        user: User,
        is_online: bool,
    ):
        profile = (
            DeliveryStatusService
            .get_profile(user)
        )

        # Safety
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Delivery account is disabled",
            )

        if not profile.is_approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Delivery account is not approved",
            )



        if not is_online:

            has_active = (
                await DeliveryStatusService
                .has_active_delivery(
                    db,
                    user,
                )
            )

            if has_active:
                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "You cannot go offline "
                        "while an active delivery exists"
                    ),
                )
        profile.is_online = is_online

        # If offline, cannot be available
        if not is_online:
            profile.is_available = False

        # If online, make available by default
        else:
            profile.is_available = True

        await db.commit()
        await db.refresh(profile)

        return profile


    # =========================================================
    # AVAILABILITY
    # =========================================================

    @staticmethod
    async def set_availability(
        db: AsyncSession,
        user: User,
        is_available: bool,
    ):
        profile = (
            DeliveryStatusService
            .get_profile(user)
        )

        if not profile.is_online:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Delivery partner must be online "
                    "before changing availability"
                ),
            )



        if is_available:

            has_active = (
                await DeliveryStatusService
                .has_active_delivery(
                    db,
                    user,
                )
            )

            if has_active:
                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "You cannot become available "
                        "while an active delivery exists"
                    ),
                )
                
                
        profile.is_available = (
            is_available
        )

        await db.commit()
        await db.refresh(profile)

        return profile


    # =========================================================
    # UPDATE LOCATION
    # =========================================================

    @staticmethod
    async def update_location(
        db: AsyncSession,
        user: User,
        latitude: float,
        longitude: float,
    ):
        profile = (
            DeliveryStatusService
            .get_profile(user)
        )

        if not profile.is_online:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Location can only be updated "
                    "while delivery partner is online"
                ),
            )

        profile.current_latitude = latitude
        profile.current_longitude = longitude

        profile.last_location_at = (
            datetime.now(
                timezone.utc
            )
        )

        await db.commit()
        await db.refresh(profile)

        return profile
    
    
    
    


    @staticmethod
    async def has_active_delivery(
        db: AsyncSession,
        user: User,
    ) -> bool:

        active_statuses = [
            "ASSIGNED",
            "ACCEPTED",
            "PICKED_UP",
            "OUT_FOR_DELIVERY",
        ]

        result = await db.execute(
            select(
                DeliveryAssignment.id
            )
            .where(
                DeliveryAssignment
                .delivery_partner_id
                == user.id,

                DeliveryAssignment
                .status
                .in_(
                    active_statuses
                ),
            )
            .limit(1)
        )

        return (
            result.scalar_one_or_none()
            is not None
        )
        
        



    async def update_online_status(
        db,
        user,
        is_online: bool,
    ):
        profile = user.delivery_profile

        if not is_online:
            active_count = (
                await DeliveryAssignmentService
                .get_active_delivery_count(
                    db,
                    user.id,
                )
            )

            if active_count > 0:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"You have {active_count} active "
                        "deliveries. Complete them "
                        "before going offline."
                    ),
                )

            profile.is_online = False
            profile.is_available = False

        else:
            profile.is_online = True

            active_count = (
                await DeliveryAssignmentService
                .get_active_delivery_count(
                    db,
                    user.id,
                )
            )

            profile.is_available = (
                active_count == 0
            )

        await db.commit()
        await db.refresh(profile)

        return profile
    


    async def update_availability(
        db,
        user,
        is_available: bool,
    ):
        profile = user.delivery_profile

        if not profile.is_online:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Go online before changing "
                    "availability"
                ),
            )

        if is_available:
            active_count = (
                await DeliveryAssignmentService
                .get_active_delivery_count(
                    db,
                    user.id,
                )
            )

            if active_count > 0:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"You have {active_count} active "
                        "deliveries."
                    ),
                )

        profile.is_available = is_available

        await db.commit()
        await db.refresh(profile)

        return profile
    
    
    

