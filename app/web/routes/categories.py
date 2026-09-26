from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
)
from app.services.category_service import (
    CategoryService,
)
from app.services.cloudinary_service import (
    CloudinaryService,
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

router = APIRouter()


# ---------------------------------------------
# Category List
# ---------------------------------------------

@router.get("/categories")
async def category_list(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = CategoryRepository(db)

    categories = await repository.get_all()

    return templates.TemplateResponse(
        request=request,
        name="admin/categories/list.html",
        context={
            "admin": current_admin,
            "categories": categories,
            "active_page": "categories",
        },
    )


# ---------------------------------------------
# Create Page
# ---------------------------------------------

@router.get("/categories/create")
async def category_create_page(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = CategoryRepository(db)

    categories = await repository.get_all()

    return templates.TemplateResponse(
        request=request,
        name="admin/categories/form.html",
        context={
            "admin": current_admin,
            "category": None,
            "categories": categories,
            "active_page": "categories",
            "error": None,
        },
    )


# ---------------------------------------------
# Create Submit
# ---------------------------------------------

@router.post("/categories/create", dependencies=[
        Depends(validate_csrf)
    ],)
async def category_create(
    request: Request,

    name: str = Form(...),

    description: str | None = Form(
        default=None
    ),

    parent_id: str | None = Form(
        default=None
    ),

    sort_order: int = Form(
        default=0
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CategoryService(db)

    try:

        data = CategoryCreate(
            name=name,
            description=(
                description or None
            ),
            parent_id=(
                int(parent_id)
                if parent_id
                else None
            ),
            sort_order=sort_order,
        )

        await service.create(data)

        return RedirectResponse(
            url="/admin/categories",
            status_code=303,
        )

    except HTTPException as exc:

        repository = CategoryRepository(db)

        categories = (
            await repository.get_all()
        )

        return templates.TemplateResponse(
            request=request,
            name="admin/categories/form.html",
            context={
                "admin": current_admin,
                "category": None,
                "categories": categories,
                "active_page": "categories",
                "error": exc.detail,
            },
            status_code=exc.status_code,
        )


# ---------------------------------------------
# Edit Page
# ---------------------------------------------

@router.get("/categories/{category_id}/edit")
async def category_edit_page(
    category_id: int,
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
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

    categories = await repository.get_all()

    return templates.TemplateResponse(
        request=request,
        name="admin/categories/form.html",
        context={
            "admin": current_admin,
            "category": category,
            "categories": categories,
            "active_page": "categories",
            "error": None,
        },
    )


# ---------------------------------------------
# Edit Submit
# ---------------------------------------------

@router.post("/categories/{category_id}/edit", dependencies=[
        Depends(validate_csrf)
    ],)
async def category_edit(
    category_id: int,
    request: Request,

    name: str = Form(...),

    description: str | None = Form(
        default=None
    ),

    parent_id: str | None = Form(
        default=None
    ),

    sort_order: int = Form(
        default=0
    ),

    is_active: str | None = Form(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CategoryService(db)

    try:

        data = CategoryUpdate(
            name=name,

            description=(
                description or None
            ),

            parent_id=(
                int(parent_id)
                if parent_id
                else None
            ),

            sort_order=sort_order,

            is_active=(
                is_active == "on"
            ),
        )

        await service.update(
            category_id,
            data,
        )

        return RedirectResponse(
            url="/admin/categories",
            status_code=303,
        )

    except HTTPException as exc:

        repository = CategoryRepository(db)

        category = (
            await repository.get_by_id(
                category_id
            )
        )

        categories = (
            await repository.get_all()
        )

        return templates.TemplateResponse(
            request=request,
            name="admin/categories/form.html",
            context={
                "admin": current_admin,
                "category": category,
                "categories": categories,
                "active_page": "categories",
                "error": exc.detail,
            },
            status_code=exc.status_code,
        )


# ---------------------------------------------
# Category Image
# ---------------------------------------------

@router.post(
    "/categories/{category_id}/image"
)
async def category_image(
    category_id: int,

    file: UploadFile = File(...),

    current_admin: User = Depends(
        get_admin_web_user
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

    if old_public_id:

        await CloudinaryService.delete_image(
            old_public_id
        )

    return RedirectResponse(
        url=f"/admin/categories/{category_id}/edit",
        status_code=303,
    )


# ---------------------------------------------
# Deactivate
# ---------------------------------------------

@router.post(
    "/categories/{category_id}/deactivate"
)
async def category_deactivate(
    category_id: int,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CategoryService(db)

    await service.deactivate(
        category_id
    )

    return RedirectResponse(
        url="/admin/categories",
        status_code=303,
    )