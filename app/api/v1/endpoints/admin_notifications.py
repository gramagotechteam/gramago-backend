from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.session import (
    get_db,
)

from app.dependencies.auth import (
    require_admin,
)

from app.models.user import (
    User,
)

from app.services.broadcast_notification_service import (
    BroadcastNotificationService,
)


router = APIRouter()


# @router.post("/test-broadcast")
# async def test_public_broadcast(

#     current_admin:
#         User = Depends(
#             require_admin
#         ),

#     db:
#         AsyncSession
#         = Depends(get_db),
# ):

#     service = (
#         BroadcastNotificationService(
#             db
#         )
#     )


#     result = (
#         await service.send(

#             notification_type=(
#                 "PROMOTION_TEST"
#             ),

#             category=(
#                 "PROMOTIONS"
#             ),

#             title=(
#                 "GramaGo Offer 🎉"
#             ),

#             message=(
#                 "Public notifications are "
#                 "working successfully."
#             ),

#             action="OPEN_HOME",
#         )
#     )


#     return {

#         "success":
#             result.get(
#                 "success",
#                 False,
#             ),

#         "message":
#             "Broadcast processed",

#         "data":
#             result,
#     }






@router.post("/test-broadcast")
async def test_broadcast_notification(
    current_admin: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    service = BroadcastNotificationService(
        db
    )

    result = await service.send(

        notification_type="PRICE_DROP",

        category="PRICE_ALERTS",

        title="Price Drop 🔥",

        message="A product price just dropped. Tap to view it.",

        action="OPEN_PRODUCT",

        reference_type="PRODUCT",

        reference_id=2,
    )

    return {
        "success": True,
        "message": "Broadcast test sent",
        "data": result,
    }