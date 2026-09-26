# from fastapi import (
#     APIRouter,
#     Depends,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db
# from app.schemas.commerce_settings import (
#     CommerceSettingsResponse,
# )
# from app.services.commerce_settings_service import (
#     CommerceSettingsService,
# )


# router = APIRouter()


# @router.get("/settings")
# async def get_public_commerce_settings(
#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

#     service = CommerceSettingsService(
#         db
#     )

#     settings = await service.get_settings()

#     return {
#         "success": True,
#         "message": (
#             "Commerce settings fetched successfully"
#         ),
#         "data": (
#             CommerceSettingsResponse
#             .model_validate(
#                 settings
#             )
#         ),
#     }
from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.commerce_settings import (
    CommerceSettingsResponse,
)
from app.services.commerce_settings_service import (
    CommerceSettingsService,
)


router = APIRouter()


# ============================================================
# PUBLIC COMMERCE SETTINGS
#
# Accessible by:
# - Guest users
# - Logged-in customers
# - Admins
#
# No authentication dependency intentionally.
# ============================================================

@router.get(
    "/settings",
)
async def get_public_commerce_settings(
    db: AsyncSession = Depends(
        get_db
    ),
):

    service = CommerceSettingsService(
        db
    )

    settings = await service.get_settings()

    return {
        "success": True,

        "message": (
            "Commerce settings fetched successfully"
        ),

        "data": (
            CommerceSettingsResponse
            .model_validate(
                settings
            )
        ),
    }