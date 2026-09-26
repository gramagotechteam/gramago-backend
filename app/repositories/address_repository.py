from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_address import (
    UserAddress,
)


class AddressRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    async def get_by_id(
        self,
        address_id: int,
    ) -> UserAddress | None:

        result = await self.db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id
            )
        )

        return result.scalar_one_or_none()


    async def get_user_address(
        self,
        address_id: int,
        user_id: int,
    ) -> UserAddress | None:

        result = await self.db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id,
                UserAddress.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()


    async def list_for_user(
        self,
        user_id: int,
    ):

        result = await self.db.execute(
            select(UserAddress)
            .where(
                UserAddress.user_id == user_id,
                UserAddress.is_active.is_(True),
            )
            .order_by(
                UserAddress.is_default.desc(),
                UserAddress.created_at.desc(),
            )
        )

        return result.scalars().all()


    async def clear_default(
        self,
        user_id: int,
    ):

        await self.db.execute(
            update(UserAddress)
            .where(
                UserAddress.user_id == user_id,
                UserAddress.is_default.is_(True),
            )
            .values(
                is_default=False
            )
        )