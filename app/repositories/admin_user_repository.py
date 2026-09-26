from sqlalchemy import (
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class AdminUserRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    async def list_admins(
        self,
        search: str | None = None,
    ):

        stmt = (
            select(User)
            .where(
                User.role.in_(
                    [
                        "ADMIN",
                        "SUPER_ADMIN",
                    ]
                )
            )
        )

        if search:

            keyword = (
                f"%{search.strip()}%"
            )

            stmt = stmt.where(
                or_(
                    User.full_name.ilike(
                        keyword
                    ),
                    User.email.ilike(
                        keyword
                    ),
                    User.phone.ilike(
                        keyword
                    ),
                )
            )

        stmt = stmt.order_by(
            User.created_at.desc()
        )

        result = await self.db.execute(
            stmt
        )

        return result.scalars().all()


    async def get_by_id(
        self,
        user_id: int,
    ):

        result = await self.db.execute(
            select(User)
            .where(
                User.id == user_id,
                User.role.in_(
                    [
                        "ADMIN",
                        "SUPER_ADMIN",
                    ]
                ),
            )
        )

        return result.scalar_one_or_none()