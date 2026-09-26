from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.schemas.category import (
    CategoryResponse,
)


router = APIRouter()


@router.get("")
async def list_categories(
    db: AsyncSession = Depends(get_db),
):

    repository = CategoryRepository(
        db
    )

    categories = (
        await repository.get_all_active()
    )

    return {
        "success": True,
        "message": "Categories fetched successfully",
        "data": [
            CategoryResponse.model_validate(
                category
            )
            for category in categories
        ],
    }