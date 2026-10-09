from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.models.user import User

from app.schemas.delivery_device_token import (
    DeliveryDeviceTokenCreate,
    DeliveryDeviceTokenDelete,
)

from app.services.delivery_device_token_service import (
    DeliveryDeviceTokenService,
)

from app.dependencies.delivery_auth import (
    get_current_delivery_partner,
)


router = APIRouter()


# ============================================================
# REGISTER DELIVERY FCM TOKEN
# ============================================================

@router.post(
    "/device-token"
)
async def register_delivery_device_token(
    data: DeliveryDeviceTokenCreate,

    current_user: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    token = (
        await DeliveryDeviceTokenService
        .register_token(
            db=db,

            user=current_user,

            token=data.token,

            platform=data.platform,
        )
    )

    return {
        "success": True,

        "message": (
            "Delivery notification token "
            "registered successfully"
        ),

        "data": {
            "id": token.id,

            "platform": (
                token.platform
            ),

            "is_active": (
                token.is_active
            ),
        },
    }


# ============================================================
# REMOVE / DEACTIVATE DELIVERY FCM TOKEN
# ============================================================

@router.delete(
    "/device-token"
)
async def remove_delivery_device_token(
    data: DeliveryDeviceTokenDelete,

    current_user: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    await DeliveryDeviceTokenService.deactivate_token(
        db=db,

        user=current_user,

        token=data.token,
    )

    return {
        "success": True,

        "message": (
            "Delivery notification token "
            "removed successfully"
        ),

        "data": None,
    }