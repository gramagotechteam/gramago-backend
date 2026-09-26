from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)
from fastapi.responses import (
    RedirectResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.admin_customer_repository import (
    AdminCustomerRepository,
)
from app.services.admin_customer_service import (
    AdminCustomerService,
)
from app.web.dependencies import (
    get_admin_web_user,
)
# from app.web.templates import templates

from app.web.templates import templates

# from fastapi.templating import (
#     Jinja2Templates,
# )


# templates = Jinja2Templates(
#     directory="app/templates"
# )


router = APIRouter()


# ==========================================
# Customer List
# ==========================================

@router.get("/customers")
async def customer_list(
    request: Request,

    search: str | None = Query(
        default=None
    ),

    status_filter: str | None = Query(
        default=None
    ),

    page: int = Query(
        default=1,
        ge=1,
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = (
        AdminCustomerRepository(db)
    )


    active_filter = None

    if status_filter == "active":

        active_filter = True

    elif status_filter == "inactive":

        active_filter = False


    customers, total = (
        await repository.list_customers(
            search=search,
            is_active=active_filter,
            page=page,
            limit=limit,
        )
    )


    total_pages = (
        ceil(total / limit)
        if total > 0
        else 0
    )


    return templates.TemplateResponse(
        request=request,
        name="admin/customers/list.html",
        context={
            "admin": current_admin,

            "customers": customers,

            "search": (
                search or ""
            ),

            "status_filter": (
                status_filter or ""
            ),

            "page": page,
            "limit": limit,
            "total": total,

            "total_pages": (
                total_pages
            ),

            "active_page": (
                "customers"
            ),
        },
    )


# ==========================================
# Customer Detail
# ==========================================

@router.get(
    "/customers/{user_id}"
)
async def customer_detail(
    user_id: int,
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = (
        AdminCustomerRepository(db)
    )


    customer = (
        await repository.get_customer(
            user_id
        )
    )


    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )


    addresses = (
        await repository.get_addresses(
            user_id
        )
    )


    orders = (
        await repository.get_orders(
            user_id,
            limit=50,
        )
    )


    stats = (
        await repository.get_stats(
            user_id
        )
    )


    return templates.TemplateResponse(
        request=request,
        name="admin/customers/detail.html",
        context={
            "admin": current_admin,

            "customer": customer,

            "addresses": addresses,

            "orders": orders,

            "stats": stats,

            "active_page": (
                "customers"
            ),
        },
    )


# ==========================================
# Deactivate
# ==========================================

@router.post(
    "/customers/{user_id}/deactivate"
)
async def customer_deactivate(
    user_id: int,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = (
        AdminCustomerService(db)
    )

    await service.deactivate(
        user_id=user_id,
        admin_id=current_admin.id,
    )

    return RedirectResponse(
        url=(
            f"/admin/customers/"
            f"{user_id}"
        ),
        status_code=303,
    )


# ==========================================
# Activate
# ==========================================

@router.post(
    "/customers/{user_id}/activate"
)
async def customer_activate(
    user_id: int,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = (
        AdminCustomerService(db)
    )

    await service.activate(
        user_id=user_id,
        admin_id=current_admin.id,
    )

    return RedirectResponse(
        url=(
            f"/admin/customers/"
            f"{user_id}"
        ),
        status_code=303,
    )