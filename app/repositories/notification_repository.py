from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import (
    Notification,
)


class NotificationRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    async def list_for_user(
        self,
        user_id: int,
        page: int,
        limit: int,
    ):

        count_result = await self.db.execute(
            select(
                func.count(
                    Notification.id
                )
            )
            .where(
                Notification.user_id
                == user_id
            )
        )

        total = count_result.scalar_one()


        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id
                == user_id
            )
            .order_by(
                Notification.created_at.desc()
            )
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
        )

        notifications = (
            result.scalars().all()
        )

        return notifications, total


    async def get_user_notification(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification | None:

        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.id
                == notification_id,

                Notification.user_id
                == user_id,
            )
        )

        return result.scalar_one_or_none()


    async def unread_count(
        self,
        user_id: int,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(
                    Notification.id
                )
            )
            .where(
                Notification.user_id
                == user_id,

                Notification.is_read
                .is_(False),
            )
        )

        return result.scalar_one()


    async def mark_all_read(
        self,
        user_id: int,
        read_at,
    ):

        await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id
                == user_id,

                Notification.is_read
                .is_(False),
            )
            .values(
                is_read=True,
                read_at=read_at,
            )
        )