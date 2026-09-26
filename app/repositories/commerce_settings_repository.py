from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce_setting import CommerceSetting


class CommerceSettingsRepository:

    SETTINGS_ID = 1

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # =========================================================
    # GET GLOBAL SETTINGS
    # =========================================================

    async def get(
        self,
    ) -> CommerceSetting | None:

        result = await self.db.execute(
            select(CommerceSetting)
            .where(
                CommerceSetting.id
                == self.SETTINGS_ID
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # GET + ROW LOCK
    #
    # Used while admin updates settings.
    #
    # This prevents two admins from changing commercial
    # settings concurrently and causing incorrect transition
    # detection.
    # =========================================================

    async def get_for_update(
        self,
    ) -> CommerceSetting | None:

        result = await self.db.execute(
            select(CommerceSetting)
            .where(
                CommerceSetting.id
                == self.SETTINGS_ID
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()