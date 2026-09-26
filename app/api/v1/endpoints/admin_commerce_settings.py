from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import (
    require_admin,
)
from app.models.user import User
from app.schemas.commerce_settings import (
    CommerceSettingsResponse,
    CommerceSettingsUpdate,
)
from app.services.commerce_settings_service import (
    CommerceSettingsService,
)


router = APIRouter()


# ============================================================
# GET COMMERCE SETTINGS
#
# ADMIN / SUPER_ADMIN only
# ============================================================

@router.get(
    "",
    response_model=dict,
)
async def get_commerce_settings(
    current_admin: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = (
        CommerceSettingsService(
            db
        )
    )

    settings = (
        await service.get_settings()
    )

    return {
        "success": True,

        "message": (
            "Commerce settings fetched "
            "successfully"
        ),

        "data": (
            CommerceSettingsResponse
            .model_validate(
                settings
            )
        ),
    }


# ============================================================
# UPDATE COMMERCE SETTINGS
#
# ADMIN / SUPER_ADMIN only
# ============================================================

@router.patch(
    "",
    response_model=dict,
)
async def update_commerce_settings(
    data: CommerceSettingsUpdate,

    current_admin: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = (
        CommerceSettingsService(
            db
        )
    )

    (
        settings,
        became_free_delivery,
    ) = await service.update_settings(
        minimum_order_amount=(
            data.minimum_order_amount
        ),

        delivery_fee=(
            data.delivery_fee
        ),

        updated_by=(
            current_admin.id
        ),
    )

    return {
        "success": True,

        "message": (
            "Commerce settings updated "
            "successfully"
        ),

        "data": {
            "settings": (
                CommerceSettingsResponse
                .model_validate(
                    settings
                )
            ),

            # Temporary internal/API information.
            #
            # Later our notification integration can use
            # this transition inside the service/API.
            "became_free_delivery": (
                became_free_delivery
            ),
        },
    }