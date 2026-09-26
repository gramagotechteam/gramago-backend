from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import (
    CategoryRepository,
    
)


from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
)
from app.utils.slug import generate_slug


class CategoryService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.categories = CategoryRepository(
            db
        )


    async def create(
        self,
        data: CategoryCreate,
    ) -> Category:

        slug = generate_slug(
            data.name
        )

        existing = (
            await self.categories.get_by_slug(
                slug
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists",
            )

        if data.parent_id:

            parent = (
                await self.categories.get_by_id(
                    data.parent_id
                )
            )

            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found",
                )

        category = Category(
            name=data.name.strip(),
            slug=slug,
            description=data.description,
            parent_id=data.parent_id,
            sort_order=data.sort_order,
        )

        self.db.add(category)

        await self.db.commit()
        await self.db.refresh(category)

        return category
    
    
    
    async def update(
    self,
    category_id: int,
    data: CategoryUpdate,
    ) -> Category:

        category = await self.categories.get_by_id(
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if data.parent_id == category.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent",
            )

        if data.parent_id is not None:

            parent = await self.categories.get_by_id(
                data.parent_id
            )

            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found",
                )

            category.parent_id = data.parent_id

        if data.name is not None:

            new_slug = generate_slug(
                data.name
            )

            existing = await self.categories.get_by_slug(
                new_slug
            )

            if existing and existing.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category name already exists",
                )

            category.name = data.name.strip()
            category.slug = new_slug

        if data.description is not None:
            category.description = data.description

        if data.sort_order is not None:
            category.sort_order = data.sort_order

        if data.is_active is not None:
            category.is_active = data.is_active

        await self.db.commit()
        await self.db.refresh(category)

        return category


    async def deactivate(
        self,
        category_id: int,
    ) -> Category:

        category = await self.categories.get_by_id(
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        category.is_active = False

        await self.db.commit()
        await self.db.refresh(category)

        return category