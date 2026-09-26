# from datetime import datetime, timezone

# from fastapi import (
#     HTTPException,
#     status,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.notification import (
#     Notification,
# )
# from app.repositories.notification_repository import (
#     NotificationRepository,
# )


# class NotificationService:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db

#         self.notifications = (
#             NotificationRepository(db)
#         )


#     async def create(
#         self,
#         *,
#         user_id: int,
#         notification_type: str,
#         title: str,
#         message: str,
#         reference_type: str | None = None,
#         reference_id: int | None = None,
#     ) -> Notification:

#         notification = Notification(
#             user_id=user_id,

#             notification_type=(
#                 notification_type
#             ),

#             title=title,
#             message=message,

#             reference_type=(
#                 reference_type
#             ),

#             reference_id=(
#                 reference_id
#             ),
#         )

#         self.db.add(notification)

#         return notification


#     async def mark_read(
#         self,
#         user_id: int,
#         notification_id: int,
#     ):

#         notification = (
#             await self.notifications
#             .get_user_notification(
#                 notification_id,
#                 user_id,
#             )
#         )

#         if not notification:

#             raise HTTPException(
#                 status_code=(
#                     status.HTTP_404_NOT_FOUND
#                 ),
#                 detail="Notification not found",
#             )

#         if not notification.is_read:

#             notification.is_read = True

#             notification.read_at = (
#                 datetime.now(
#                     timezone.utc
#                 )
#             )

#             await self.db.commit()

#             await self.db.refresh(
#                 notification
#             )

#         return notification


#     async def mark_all_read(
#         self,
#         user_id: int,
#     ):

#         now = datetime.now(
#             timezone.utc
#         )

#         await self.notifications.mark_all_read(
#             user_id,
#             now,
#         )

#         await self.db.commit()





from datetime import (
    datetime,
    timezone,
)

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.notification import (
    Notification,
)

from app.repositories.notification_repository import (
    NotificationRepository,
)

from app.repositories.notification_preference_repository import (
    NotificationPreferenceRepository,
)

from app.services.push_notification_service import (
    PushNotificationService,
)


class NotificationService:

    CATEGORY_TRANSACTIONAL = (
        "TRANSACTIONAL"
    )

    CATEGORY_PRODUCTS = (
        "PRODUCTS"
    )

    CATEGORY_PRICE_ALERTS = (
        "PRICE_ALERTS"
    )

    CATEGORY_PROMOTIONS = (
        "PROMOTIONS"
    )

    CATEGORY_GENERAL = (
        "GENERAL"
    )


    def __init__(
        self,
        db: AsyncSession,
    ):

        self.db = db


        self.notifications = (
            NotificationRepository(
                db
            )
        )


        self.preferences = (
            NotificationPreferenceRepository(
                db
            )
        )


        self.push = (
            PushNotificationService(
                db
            )
        )


    # =========================================================
    # CREATE IN-APP NOTIFICATION
    #
    # Does NOT commit.
    # Does NOT send push yet.
    #
    # This is intentional so order/product DB operations
    # remain atomic.
    # =========================================================

    async def create(
        self,
        *,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        category: str = "GENERAL",
        action: str = "OPEN_NOTIFICATIONS",
        reference_type: str | None = None,
        reference_id: int | None = None,
        image_url: str | None = None,
        metadata: dict | None = None,
    ) -> Notification:

        notification = Notification(

            user_id=user_id,


            notification_type=(
                notification_type
            ),


            category=category,


            title=title,

            message=message,


            action=action,


            reference_type=(
                reference_type
            ),


            reference_id=(
                reference_id
            ),


            image_url=image_url,


            metadata_json=(
                metadata
            ),
        )


        self.db.add(
            notification
        )


        await self.db.flush()


        return notification


    # =========================================================
    # PUSH AFTER DB COMMIT
    # =========================================================

    async def dispatch(
        self,
        notification: Notification,
    ) -> dict:

        if not await self._push_allowed(
            user_id=notification.user_id,
            category=notification.category,
        ):

            return {
                "success": True,
                "sent": 0,
                "failed": 0,
                "reason":
                    "Disabled by user preference",
            }


        channel = (
            self._channel_for_category(
                notification.category
            )
        )


        data = {

            "notification_id":
                notification.id,

            "type":
                notification.notification_type,

            "category":
                notification.category,

            "action":
                notification.action,

            "reference_type":
                notification.reference_type,

            "reference_id":
                notification.reference_id,
        }


        if notification.metadata_json:

            for key, value in (
                notification.metadata_json.items()
            ):

                if key not in data:
                    data[key] = value


        return await self.push.send_to_user(

            user_id=(
                notification.user_id
            ),

            title=(
                notification.title
            ),

            body=(
                notification.message
            ),

            image_url=(
                notification.image_url
            ),

            channel_id=channel,

            data=data,
        )


    # =========================================================
    # CREATE + COMMIT + PUSH
    #
    # Useful for standalone events / testing.
    # =========================================================

    async def notify_user(
        self,
        *,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        category: str = "GENERAL",
        action: str = "OPEN_NOTIFICATIONS",
        reference_type: str | None = None,
        reference_id: int | None = None,
        image_url: str | None = None,
        metadata: dict | None = None,
    ) -> Notification:

        notification = await self.create(

            user_id=user_id,

            notification_type=(
                notification_type
            ),

            title=title,

            message=message,

            category=category,

            action=action,

            reference_type=(
                reference_type
            ),

            reference_id=(
                reference_id
            ),

            image_url=image_url,

            metadata=metadata,
        )


        await self.db.commit()


        await self.db.refresh(
            notification
        )


        await self.dispatch(
            notification
        )


        return notification


    # =========================================================
    # READ
    # =========================================================

    async def mark_read(
        self,
        user_id: int,
        notification_id: int,
    ):

        notification = (
            await self.notifications
            .get_user_notification(
                notification_id,
                user_id,
            )
        )


        if not notification:

            raise HTTPException(

                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),

                detail=(
                    "Notification not found"
                ),
            )


        if not notification.is_read:

            notification.is_read = True


            notification.read_at = (
                datetime.now(
                    timezone.utc
                )
            )


            await self.db.commit()


            await self.db.refresh(
                notification
            )


        return notification


    async def mark_all_read(
        self,
        user_id: int,
    ):

        now = datetime.now(
            timezone.utc
        )


        await self.notifications.mark_all_read(
            user_id,
            now,
        )


        await self.db.commit()


    # =========================================================
    # PREFERENCE CHECK
    # =========================================================

    async def _push_allowed(
        self,
        *,
        user_id: int,
        category: str,
    ) -> bool:

        preference = (
            await self.preferences
            .get_or_create(
                user_id
            )
        )


        if (
            category
            == self.CATEGORY_TRANSACTIONAL
        ):

            return (
                preference
                .transactional_enabled
            )


        if (
            category
            == self.CATEGORY_PRODUCTS
        ):

            return (
                preference
                .product_updates_enabled
            )


        if (
            category
            == self.CATEGORY_PRICE_ALERTS
        ):

            return (
                preference
                .price_alerts_enabled
            )


        if (
            category
            == self.CATEGORY_PROMOTIONS
        ):

            return (
                preference
                .promotions_enabled
            )


        return (
            preference.general_enabled
        )


    # =========================================================
    # ANDROID CHANNEL
    # =========================================================

    def _channel_for_category(
        self,
        category: str,
    ) -> str:

        if (
            category
            == self.CATEGORY_TRANSACTIONAL
        ):

            return "gramago_orders"


        if (
            category
            == self.CATEGORY_PRODUCTS
        ):

            return "gramago_products"


        if (
            category
            == self.CATEGORY_PRICE_ALERTS
        ):

            return "gramago_offers"


        if (
            category
            == self.CATEGORY_PROMOTIONS
        ):

            return "gramago_offers"


        return "gramago_general"