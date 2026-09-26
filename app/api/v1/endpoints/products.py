# from fastapi import (
#     APIRouter,
#     Depends,
#     HTTPException,
#     status,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db
# from app.repositories.product_repository import (
#     ProductRepository,
# )
# from app.schemas.product import (
#     ProductResponse,
# )


# router = APIRouter()


from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.product_repository import (
    ProductRepository,
)
from app.schemas.product import (
    ProductDetailResponse,
)


router = APIRouter()


@router.get("")
async def list_products(
    search: str | None = Query(
        default=None,
        max_length=100,
    ),

    category_id: int | None = Query(
        default=None,
        ge=1,
    ),

    featured: bool | None = None,

    in_stock: bool | None = None,

    page: int = Query(
        default=1,
        ge=1,
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = ProductRepository(
        db
    )

    products, total = (
        await repository.search(
            search=search,
            category_id=category_id,
            featured=featured,
            in_stock=in_stock,
            page=page,
            limit=limit,
        )
    )

    total_pages = (
        ceil(total / limit)
        if total > 0
        else 0
    )

    return {
        "success": True,
        "message": "Products fetched successfully",
        "data": [
            ProductDetailResponse.model_validate(
                product
            )
            for product in products
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total,
            "total_pages": total_pages,
        },
    }



# @router.get("/{product_id}")
# async def get_product(
#     product_id: int,
#     db: AsyncSession = Depends(get_db),
# ):

#     repository = ProductRepository(
#         db
#     )

#     product = await repository.get_by_id(
#         product_id
#     )

#     if not product or not product.is_active:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Product not found",
#         )

#     return {
#         "success": True,
#         "message": "Product fetched successfully",
#         "data": ProductResponse.model_validate(
#             product
#         ),
#     }



@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):

    repository = ProductRepository(
        db
    )

    product = await repository.get_by_id(
        product_id,
        include_relations=True,
    )

    if (
        not product
        or not product.is_active
    ):

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return {
        "success": True,
        "message": "Product fetched successfully",
        "data": (
            ProductDetailResponse
            .model_validate(product)
        ),
    }