from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.session import get_db

from app.dependencies.delivery_auth import (
    get_current_delivery_partner,
)

from app.models.user import User

from app.schemas.delivery_status import (
    DeliveryOnlineStatusUpdate,
    DeliveryAvailabilityUpdate,
    DeliveryLocationUpdate,
)

from app.services.delivery_status_service import (
    DeliveryStatusService,
)


router = APIRouter()


# ============================================================
# GET STATUS
# ============================================================

@router.get("")
async def get_delivery_status(
    current_partner: User = Depends(
        get_current_delivery_partner
    ),
):
    profile = (
        DeliveryStatusService
        .get_profile(
            current_partner
        )
    )

    return {
        "success": True,
        "message": (
            "Delivery status retrieved successfully"
        ),
        "data": {
            "is_online": (
                profile.is_online
            ),

            "is_available": (
                profile.is_available
            ),

            "current_latitude": (
                float(
                    profile.current_latitude
                )
                if profile.current_latitude
                is not None
                else None
            ),

            "current_longitude": (
                float(
                    profile.current_longitude
                )
                if profile.current_longitude
                is not None
                else None
            ),

            "last_location_at": (
                profile.last_location_at
            ),
        },
    }


# ============================================================
# ONLINE / OFFLINE
# ============================================================

@router.patch("/online")
async def update_online_status(
    data: DeliveryOnlineStatusUpdate,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    profile = (
        await DeliveryStatusService
        .set_online_status(
            db,
            current_partner,
            data.is_online,
        )
    )

    return {
        "success": True,
        "message": (
            "You are now online"
            if profile.is_online
            else "You are now offline"
        ),
        "data": {
            "is_online": (
                profile.is_online
            ),

            "is_available": (
                profile.is_available
            ),
        },
    }


# ============================================================
# AVAILABLE / BUSY
# ============================================================

@router.patch("/availability")
async def update_availability(
    data: DeliveryAvailabilityUpdate,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    profile = (
        await DeliveryStatusService
        .set_availability(
            db,
            current_partner,
            data.is_available,
        )
    )

    return {
        "success": True,
        "message": (
            "Availability updated successfully"
        ),
        "data": {
            "is_online": (
                profile.is_online
            ),

            "is_available": (
                profile.is_available
            ),
        },
    }


# ============================================================
# LOCATION
# ============================================================

@router.post("/location")
async def update_location(
    data: DeliveryLocationUpdate,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    profile = (
        await DeliveryStatusService
        .update_location(
            db,
            current_partner,
            data.latitude,
            data.longitude,
        )
    )

    return {
        "success": True,
        "message": (
            "Location updated successfully"
        ),
        "data": {
            "latitude": float(
                profile.current_latitude
            ),

            "longitude": float(
                profile.current_longitude
            ),

            "last_location_at": (
                profile.last_location_at
            ),
        },
    }