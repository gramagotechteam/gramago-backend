from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User
from app.repositories.notification_repository import (
    NotificationRepository,
)
from app.schemas.notification import (
    NotificationResponse,
)
from app.services.notification_service import (
    NotificationService,
)

from app.repositories.notification_preference_repository import (
    NotificationPreferenceRepository,
)

from app.schemas.notification import (
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)

from app.db.session import get_db
from app.dependencies.auth import require_admin

from app.models.user import User

from app.schemas.notification import (
    NotificationResponse,
)

from app.services.notification_service import (
    NotificationService,
)

from pydantic import BaseModel

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import require_admin


router = APIRouter()


class TestPushRequest(BaseModel):
    user_id: int




@router.get("")
async def list_notifications(
    page: int = Query(
        default=1,
        ge=1,
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = (
        NotificationRepository(db)
    )

    notifications, total = (
        await repository.list_for_user(
            current_user.id,
            page,
            limit,
        )
    )

    return {
        "success": True,
        "message": (
            "Notifications fetched successfully"
        ),
        "data": [
            NotificationResponse.model_validate(
                item
            )
            for item in notifications
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total,
            "total_pages": (
                ceil(total / limit)
                if total
                else 0
            ),
        },
    }
    
    
    

@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = (
        NotificationRepository(db)
    )

    count = await repository.unread_count(
        current_user.id
    )

    return {
        "success": True,
        "message": "Unread count fetched",
        "data": {
            "unread_count": count
        },
    }
    


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = NotificationService(db)

    notification = (
        await service.mark_read(
            current_user.id,
            notification_id,
        )
    )

    return {
        "success": True,
        "message": "Notification marked as read",
        "data": (
            NotificationResponse
            .model_validate(notification)
        ),
    }
    




@router.patch("/read-all")
async def mark_all_read(
    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = NotificationService(db)

    await service.mark_all_read(
        current_user.id
    )

    return {
        "success": True,
        "message": (
            "All notifications marked as read"
        ),
        "data": None,
    }
    
    


# ============================================================
# GET PREFERENCES
# ============================================================

@router.get("/preferences")
async def get_notification_preferences(

    current_user:
        User = Depends(
            get_current_user
        ),

    db:
        AsyncSession = Depends(
            get_db
        ),
):

    repository = (
        NotificationPreferenceRepository(
            db
        )
    )


    preference = (
        await repository.get_or_create(
            current_user.id
        )
    )


    await db.commit()


    return {

        "success": True,

        "message":
            "Notification preferences fetched",

        "data":
            NotificationPreferenceResponse
            .model_validate(
                preference
            ),
    }


# ============================================================
# UPDATE PREFERENCES
# ============================================================

@router.patch("/preferences")
async def update_notification_preferences(

    payload:
        NotificationPreferenceUpdate,

    current_user:
        User = Depends(
            get_current_user
        ),

    db:
        AsyncSession = Depends(
            get_db
        ),
):

    repository = (
        NotificationPreferenceRepository(
            db
        )
    )


    preference = (
        await repository.get_or_create(
            current_user.id
        )
    )


    updates = (
        payload.model_dump(
            exclude_unset=True
        )
    )


    for field, value in updates.items():

        setattr(
            preference,
            field,
            value,
        )


    await db.commit()


    await db.refresh(
        preference
    )


    return {

        "success": True,

        "message":
            "Notification preferences updated",

        "data":
            NotificationPreferenceResponse
            .model_validate(
                preference
            ),
    }
    
    




# @router.post("/test-push")
# async def test_push_notification(
#     payload: TestPushRequest,

#     current_admin: User = Depends(
#         require_admin
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

@router.post("/test-push")
async def test_push_notification(
    payload: TestPushRequest,

    current_admin: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    # =========================================================
    # 1. CHECK TARGET USER EXISTS
    # =========================================================

    result = await db.execute(
        select(User).where(
            User.id == payload.user_id
        )
    )

    target_user = (
        result.scalar_one_or_none()
    )


    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="Target user not found",
        )


    # =========================================================
    # 2. CREATE NOTIFICATION FOR TARGET USER
    # =========================================================

    service = NotificationService(
        db
    )


    # notification = await service.create(

    #     user_id=target_user.id,

    #     notification_type="SYSTEM_TEST",

    #     category="GENERAL",

    #     title="GramaGo Notifications 🎉",

    #     message=(
    #         "Push notifications are "
    #         "working successfully."
    #     ),

    #     action="OPEN_NOTIFICATIONS",
    # )


    notification = await service.create(
    user_id=payload.user_id,
    notification_type="ORDER_CONFIRMED",
    category="ORDERS",
    title="Order Confirmed ✅",
    message="Your order has been confirmed. Tap to view the details.",
    action="OPEN_ORDER",
    reference_type="ORDER",
    reference_id=2,
)

    # =========================================================
    # 3. COMMIT DATABASE FIRST
    # =========================================================

    await db.commit()

    await db.refresh(
        notification
    )


    # =========================================================
    # 4. SEND FIREBASE PUSH
    # =========================================================

    push_result = await service.dispatch(
        notification
    )


    # =========================================================
    # 5. RESPONSE
    # =========================================================

    return {
        "success": True,

        "message":
            "Test notification processed",

        "data": {

            "sent_by_admin_id":
                current_admin.id,

            "target_user_id":
                target_user.id,

            "notification":
                NotificationResponse
                .model_validate(
                    notification
                ),

            "push":
                push_result,
        },
    }