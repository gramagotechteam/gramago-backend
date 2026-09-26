from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.admin_user_repository import (
    AdminUserRepository,
)
from app.services.admin_user_service import (
    AdminUserService,
)
from app.web.csrf import validate_csrf
from app.web.dependencies import (
    get_super_admin_web_user,
)
from app.web.flash import flash
from app.web.templates import templates


router = APIRouter()


@router.get("/admin-users")
async def admin_list(
    request: Request,
    search: str | None = None,
    current_admin: User = Depends(
        get_super_admin_web_user
    ),
    db: AsyncSession = Depends(get_db),
):

    users = await AdminUserRepository(
        db
    ).list_admins(search)

    return templates.TemplateResponse(
        request=request,
        name="admin/admin_users/list.html",
        context={
            "admin": current_admin,
            "users": users,
            "search": search or "",
            "active_page": "admin_users",
        },
    )


@router.get("/admin-users/create")
async def create_page(
    request: Request,
    current_admin: User = Depends(
        get_super_admin_web_user
    ),
):

    return templates.TemplateResponse(
        request=request,
        name="admin/admin_users/create.html",
        context={
            "admin": current_admin,
            "active_page": "admin_users",
        },
    )


@router.post(
    "/admin-users/create",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def create_admin(
    request: Request,

    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),

    current_admin: User = Depends(
        get_super_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    try:

        await AdminUserService(
            db
        ).create_admin(
            full_name=full_name,
            email=email,
            phone=phone,
            password=password,
            created_by=current_admin.id,
        )

        flash(
            request,
            "Admin created successfully.",
        )

        return RedirectResponse(
            "/admin/admin-users",
            status_code=303,
        )

    except HTTPException as exc:

        flash(
            request,
            exc.detail,
            "danger",
        )

        return RedirectResponse(
            "/admin/admin-users/create",
            status_code=303,
        )