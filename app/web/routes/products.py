from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.product_image import (
    ProductImage,
)
from app.models.user import User
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.repositories.product_repository import (
    ProductRepository,
)
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
)
from app.services.cloudinary_service import (
    CloudinaryService,
)
from app.services.product_service import (
    ProductService,
)
from app.web.dependencies import (
    get_admin_web_user,
)
from app.web.templates import templates

# from fastapi.templating import (
#     Jinja2Templates,
# )


# templates = Jinja2Templates(
#     directory="app/templates"
# )

from app.web.csrf import validate_csrf

import logging

router = APIRouter()


logger = logging.getLogger(
    __name__
)

# ---------------------------------------------
# Product List
# ---------------------------------------------

@router.get("/products")
async def product_list(
    request: Request,

    search: str | None = Query(
        default=None
    ),

    category_id: int | None = Query(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    products_repo = ProductRepository(
        db
    )

    categories_repo = CategoryRepository(
        db
    )

    products = await products_repo.admin_list(
        search=search,
        category_id=category_id,
    )

    categories = (
        await categories_repo.get_all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/products/list.html",
        context={
            "admin": current_admin,
            "products": products,
            "categories": categories,
            "search": search or "",
            "selected_category": (
                category_id
            ),
            "active_page": "products",
        },
    )


# ---------------------------------------------
# Product Create Page
# ---------------------------------------------

@router.get("/products/create")
async def product_create_page(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    category_repo = (
        CategoryRepository(db)
    )

    categories = (
        await category_repo.get_all_active()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/products/form.html",
        context={
            "admin": current_admin,
            "product": None,
            "categories": categories,
            "active_page": "products",
            "error": None,
        },
    )


# ---------------------------------------------
# Product Create Submit
# ---------------------------------------------

@router.post("/products/create",
             dependencies=[
        Depends(validate_csrf)
    ],
             )
async def product_create(
    request: Request,

    category_id: int = Form(...),

    name: str = Form(...),

    sku: str | None = Form(
        default=None
    ),

    description: str | None = Form(
        default=None
    ),

    price: Decimal = Form(...),

    discount_price: str | None = Form(
        default=None
    ),

    unit: str = Form(...),

    unit_value: Decimal = Form(...),

    min_order_qty: Decimal = Form(...),

    max_order_qty: str | None = Form(
        default=None
    ),

    is_featured: str | None = Form(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = ProductService(db)

    try:

        data = ProductCreate(
            category_id=category_id,
            name=name,
            sku=sku or None,
            description=(
                description or None
            ),
            price=price,
            discount_price=(
                Decimal(
                    discount_price
                )
                if discount_price
                else None
            ),
            unit=unit,
            unit_value=unit_value,
            min_order_qty=(
                min_order_qty
            ),
            max_order_qty=(
                Decimal(
                    max_order_qty
                )
                if max_order_qty
                else None
            ),
            is_featured=(
                is_featured == "on"
            ),
        )

        product = await service.create(
            data
        )

        return RedirectResponse(
            url=(
                f"/admin/products/"
                f"{product.id}/edit"
            ),
            status_code=303,
        )

    except HTTPException as exc:

        categories = (
            await CategoryRepository(
                db
            ).get_all_active()
        )

        return templates.TemplateResponse(
            request=request,
            name="admin/products/form.html",
            context={
                "admin": current_admin,
                "product": None,
                "categories": categories,
                "active_page": "products",
                "error": exc.detail,
            },
            status_code=exc.status_code,
        )


# ---------------------------------------------
# Product Edit Page
# ---------------------------------------------

@router.get("/products/{product_id}/edit")
async def product_edit_page(
    product_id: int,
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    product_repo = ProductRepository(db)

    product = await product_repo.get_by_id(
        product_id,
        include_relations=True,
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    categories = (
        await CategoryRepository(
            db
        ).get_all_active()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/products/form.html",
        context={
            "admin": current_admin,
            "product": product,
            "categories": categories,
            "active_page": "products",
            "error": None,
        },
    )


# ---------------------------------------------
# Product Edit Submit
# ---------------------------------------------

@router.post("/products/{product_id}/edit",
             dependencies=[
        Depends(validate_csrf)
    ],
             )
async def product_edit(
    product_id: int,
    request: Request,

    category_id: int = Form(...),

    name: str = Form(...),

    sku: str | None = Form(
        default=None
    ),

    description: str | None = Form(
        default=None
    ),

    price: Decimal = Form(...),

    discount_price: str | None = Form(
        default=None
    ),

    unit: str = Form(...),

    unit_value: Decimal = Form(...),

    min_order_qty: Decimal = Form(...),

    max_order_qty: str | None = Form(
        default=None
    ),

    is_active: str | None = Form(
        default=None
    ),

    is_featured: str | None = Form(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = ProductService(db)

    try:

        data = ProductUpdate(
            category_id=category_id,
            name=name,
            sku=sku or None,
            description=(
                description or None
            ),
            price=price,

            discount_price=(
                Decimal(
                    discount_price
                )
                if discount_price
                else None
            ),

            unit=unit,

            unit_value=unit_value,

            min_order_qty=(
                min_order_qty
            ),

            max_order_qty=(
                Decimal(
                    max_order_qty
                )
                if max_order_qty
                else None
            ),

            is_active=(
                is_active == "on"
            ),

            is_featured=(
                is_featured == "on"
            ),
        )

        await service.update(
            product_id,
            data,
        )

        return RedirectResponse(
            url=(
                f"/admin/products/"
                f"{product_id}/edit"
            ),
            status_code=303,
        )

    except HTTPException as exc:

        product = (
            await ProductRepository(
                db
            ).get_by_id(
                product_id,
                include_relations=True,
            )
        )

        categories = (
            await CategoryRepository(
                db
            ).get_all_active()
        )

        return templates.TemplateResponse(
            request=request,
            name="admin/products/form.html",
            context={
                "admin": current_admin,
                "product": product,
                "categories": categories,
                "active_page": "products",
                "error": exc.detail,
            },
            status_code=exc.status_code,
        )


# ---------------------------------------------
# Upload Product Image
# ---------------------------------------------

@router.post(
    "/products/{product_id}/images"
)
async def product_image_upload(
    product_id: int,

    file: UploadFile = File(...),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    product = await ProductRepository(
        db
    ).get_by_id(
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    count_result = await db.execute(
        select(
            func.count(
                ProductImage.id
            )
        )
        .where(
            ProductImage.product_id
            == product_id
        )
    )

    count = count_result.scalar_one()

    uploaded = (
        await CloudinaryService
        .upload_product_image(
            file,
            product_id,
        )
    )

    image = ProductImage(
        product_id=product_id,

        image_url=uploaded[
            "image_url"
        ],

        cloudinary_public_id=(
            uploaded["public_id"]
        ),

        is_primary=(
            count == 0
        ),
    )

    # db.add(image)

    # await db.commit()

    # return RedirectResponse(
    #     url=(
    #         f"/admin/products/"
    #         f"{product_id}/edit"
    #     ),
    #     status_code=303,
    # )

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

    if count == 0:

        try:

            product_service = (
                ProductService(
                    db
                )
            )


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

            logger.exception(
                (
                    "Failed to send NEW_PRODUCT "
                    "broadcast after first image upload. "
                    "product_id=%s"
                ),
                product_id,
            )


    return RedirectResponse(
        url=(
            f"/admin/products/"
            f"{product_id}/edit"
        ),
        status_code=303,
    )

# ---------------------------------------------
# Set Primary Image
# ---------------------------------------------

@router.post(
    "/products/{product_id}/images/{image_id}/primary"
)
async def product_image_primary(
    product_id: int,
    image_id: int,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(ProductImage)
        .where(
            ProductImage.id == image_id,
            ProductImage.product_id
            == product_id,
        )
    )

    image = (
        result.scalar_one_or_none()
    )

    if not image:

        raise HTTPException(
            status_code=404,
            detail="Image not found",
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

    return RedirectResponse(
        url=(
            f"/admin/products/"
            f"{product_id}/edit"
        ),
        status_code=303,
    )


# ---------------------------------------------
# Delete Product Image
# ---------------------------------------------

@router.post(
    "/products/{product_id}/images/{image_id}/delete"
)
async def product_image_delete(
    product_id: int,
    image_id: int,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(ProductImage)
        .where(
            ProductImage.id == image_id,
            ProductImage.product_id
            == product_id,
        )
    )

    image = (
        result.scalar_one_or_none()
    )

    if not image:

        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )

    was_primary = image.is_primary

    public_id = (
        image.cloudinary_public_id
    )

    await db.delete(image)

    await db.flush()

    if was_primary:

        result = await db.execute(
            select(ProductImage)
            .where(
                ProductImage.product_id
                == product_id
            )
            .order_by(
                ProductImage.id
            )
            .limit(1)
        )

        next_image = (
            result.scalar_one_or_none()
        )

        if next_image:

            next_image.is_primary = True

    await db.commit()

    await CloudinaryService.delete_image(
        public_id
    )

    return RedirectResponse(
        url=(
            f"/admin/products/"
            f"{product_id}/edit"
        ),
        status_code=303,
    )


# ---------------------------------------------
# Deactivate Product
# ---------------------------------------------

@router.post(
    "/products/{product_id}/deactivate"
)
async def product_deactivate(
    product_id: int,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    await ProductService(
        db
    ).deactivate(
        product_id
    )

    return RedirectResponse(
        url="/admin/products",
        status_code=303,
    )