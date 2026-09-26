from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.notification_preference import (
    NotificationPreference,
)


class NotificationPreferenceRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.db = db


    async def get_or_create(
        self,
        user_id: int,
    ) -> NotificationPreference:

        result = await self.db.execute(

            select(
                NotificationPreference
            )

            .where(
                NotificationPreference
                .user_id
                == user_id
            )
        )


        preference = (
            result.scalar_one_or_none()
        )


        if preference:

            return preference


        preference = (
            NotificationPreference(
                user_id=user_id
            )
        )


        self.db.add(
            preference
        )


        await self.db.flush()


        return preference