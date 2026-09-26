from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    async def get_by_id(
        self,
        category_id: int,
    ) -> Category | None:

        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id
            )
        )

        return result.scalar_one_or_none()


    async def get_by_slug(
        self,
        slug: str,
    ) -> Category | None:

        result = await self.db.execute(
            select(Category).where(
                Category.slug == slug
            )
        )

        return result.scalar_one_or_none()


    async def get_all_active(
        self,
    ):

        result = await self.db.execute(
            select(Category)
            .where(
                Category.is_active.is_(True)
            )
            .order_by(
                Category.sort_order,
                Category.name,
            )
        )

        return result.scalars().all()
    
    
    async def get_all(
    self,
    ):

        result = await self.db.execute(
            select(Category)
            .order_by(
                Category.sort_order,
                Category.name,
            )
        )

        return result.scalars().all()
    
    
    