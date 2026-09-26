# from fastapi import (
#     APIRouter,
#     Depends,
#     status,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db
# from app.dependencies.auth import require_admin
# from app.models.user import User
# from app.schemas.category import (
#     CategoryCreate,
#     CategoryResponse,
# )
# from app.services.category_service import (
#     CategoryService,
# )


# router = APIRouter()


from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import (
    CategoryService,
)
from app.services.cloudinary_service import (
    CloudinaryService,
)


router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = CategoryService(db)

    category = await service.create(
        data
    )

    return {
        "success": True,
        "message": "Category created successfully",
        "data": CategoryResponse.model_validate(
            category
        ),
    }
    
    



@router.patch("/{category_id}")
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = CategoryService(db)

    category = await service.update(
        category_id,
        data,
    )

    return {
        "success": True,
        "message": "Category updated successfully",
        "data": CategoryResponse.model_validate(
            category
        ),
    }
    
    


@router.patch("/{category_id}")
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = CategoryService(db)

    category = await service.update(
        category_id,
        data,
    )

    return {
        "success": True,
        "message": "Category updated successfully",
        "data": CategoryResponse.model_validate(
            category
        ),
    }
    


@router.post("/{category_id}/image")
async def upload_category_image(
    category_id: int,

    file: UploadFile = File(...),

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = CategoryRepository(db)

    category = await repository.get_by_id(
        category_id
    )

    if not category:

        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    old_public_id = (
        category.cloudinary_public_id
    )

    uploaded = (
        await CloudinaryService
        .upload_category_image(
            file,
            category_id,
        )
    )

    category.image_url = uploaded[
        "image_url"
    ]

    category.cloudinary_public_id = (
        uploaded["public_id"]
    )

    await db.commit()
    await db.refresh(category)

    if old_public_id:

        await CloudinaryService.delete_image(
            old_public_id
        )

    return {
        "success": True,
        "message": "Category image uploaded successfully",
        "data": CategoryResponse.model_validate(
            category
        ),
    }