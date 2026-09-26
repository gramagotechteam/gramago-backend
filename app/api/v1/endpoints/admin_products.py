from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
)
from app.services.product_service import (
    ProductService,
)

from fastapi import UploadFile, File
from sqlalchemy import select

from app.models.product import Product
from app.models.product_image import ProductImage
from app.services.cloudinary_service import (
    CloudinaryService,
)

from sqlalchemy import (
    func,
    select,
    update,
    
    
    
)


import logging

logger = logging.getLogger(
    __name__
)

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):

    service = ProductService(db)

    product = await service.create(
        data
    )

    return {
        "success": True,
        "message": "Product created successfully",
        "data": ProductResponse.model_validate(
            product
        ),
    }
    



@router.post(
    "/{product_id}/images"
)
async def upload_product_image(
    product_id: int,

    file: UploadFile = File(...),

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Product).where(
            Product.id == product_id
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    upload_result = (
        await CloudinaryService
        .upload_product_image(
            file,
            product_id,
        )
    )
    count_result = await db.execute(
        select(
            func.count(ProductImage.id)
        ).where(
            ProductImage.product_id
            == product_id
        )
    )

    image_count = count_result.scalar_one()

    # image = ProductImage(
    #     product_id=product_id,
    #     image_url=upload_result[
    #         "image_url"
    #     ],
    #     cloudinary_public_id=(
    #         upload_result["public_id"]
    #     ),
    # )
    
    image = ProductImage(
        product_id=product_id,
        image_url=upload_result[
            "image_url"
        ],
        cloudinary_public_id=(
            upload_result["public_id"]
        ),
        is_primary=(
            image_count == 0
        ),
    )

    # db.add(image)

    # await db.commit()
    # await db.refresh(image)

    db.add(
        image
    )

    await db.commit()

    await db.refresh(
        image
    )


    # ============================================================
    # FIRST IMAGE → NEW PRODUCT BROADCAST
    # ============================================================

    if image_count == 0:

        try:

            product_service = (
                ProductService(
                    db
                )
            )


            # Reload product after image has been committed.
            product_with_image = (
                await product_service.products.get_by_id(
                    product_id,
                    include_relations=True,
                )
            )


            if product_with_image is not None:

                await product_service.send_new_product_broadcast(
                    product_with_image
                )


        except Exception:

            # Image upload itself must still succeed even
            # if Firebase/broadcast temporarily fails.
            import logging

            logging.getLogger(
                __name__
            ).exception(
                (
                    "Failed to send NEW_PRODUCT "
                    "broadcast after first image upload. "
                    "product_id=%s"
                ),
                product_id,
            )

    return {
        "success": True,
        "message": (
            "Product image uploaded successfully"
        ),
        "data": {
            "id": image.id,
            "image_url": image.image_url,
        },
    }



from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

@router.patch("/{product_id}")
async def update_product(
    product_id: int,
    data: ProductUpdate,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    service = ProductService(db)

    product = await service.update(
        product_id,
        data,
    )

    return {
        "success": True,
        "message": "Product updated successfully",
        "data": ProductResponse.model_validate(
            product
        ),
    }
    
    



@router.post("/{product_id}/deactivate")
async def deactivate_product(
    product_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    service = ProductService(db)

    product = await service.deactivate(
        product_id
    )

    return {
        "success": True,
        "message": "Product deactivated successfully",
        "data": ProductResponse.model_validate(
            product
        ),
    }
    


@router.get("/{product_id}/images")
async def list_product_images(
    product_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(ProductImage)
        .where(
            ProductImage.product_id
            == product_id
        )
        .order_by(
            ProductImage.sort_order,
            ProductImage.id,
        )
    )

    images = result.scalars().all()

    return {
        "success": True,
        "message": "Product images fetched successfully",
        "data": [
            {
                "id": image.id,
                "image_url": image.image_url,
                "is_primary": image.is_primary,
                "sort_order": image.sort_order,
            }
            for image in images
        ],
    }
    



@router.post(
    "/{product_id}/images/{image_id}/primary"
)
async def set_primary_image(
    product_id: int,
    image_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(ProductImage).where(
            ProductImage.id == image_id,
            ProductImage.product_id
            == product_id,
        )
    )

    image = result.scalar_one_or_none()

    if not image:

        raise HTTPException(
            status_code=404,
            detail="Product image not found",
        )

    await db.execute(
        update(ProductImage)
        .where(
            ProductImage.product_id
            == product_id
        )
        .values(
            is_primary=False
        )
    )

    image.is_primary = True

    await db.commit()

    return {
        "success": True,
        "message": "Primary image updated successfully",
        "data": {
            "image_id": image.id,
        },
    }
    




@router.delete(
    "/{product_id}/images/{image_id}"
)
async def delete_product_image(
    product_id: int,
    image_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(ProductImage).where(
            ProductImage.id == image_id,
            ProductImage.product_id
            == product_id,
        )
    )

    image = result.scalar_one_or_none()

    if not image:

        raise HTTPException(
            status_code=404,
            detail="Product image not found",
        )

    was_primary = image.is_primary

    public_id = (
        image.cloudinary_public_id
    )

    await db.delete(image)

    await db.flush()

    if was_primary:

        next_result = await db.execute(
            select(ProductImage)
            .where(
                ProductImage.product_id
                == product_id
            )
            .order_by(
                ProductImage.sort_order,
                ProductImage.id,
            )
            .limit(1)
        )

        next_image = (
            next_result.scalar_one_or_none()
        )

        if next_image:
            next_image.is_primary = True

    await db.commit()

    await CloudinaryService.delete_image(
        public_id
    )

    return {
        "success": True,
        "message": "Product image deleted successfully",
        "data": None,
    }