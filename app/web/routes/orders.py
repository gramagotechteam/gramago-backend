from math import ceil
from urllib import request
from urllib import request
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    Request,
)
from fastapi.responses import (
    RedirectResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.order_status import (
    ORDER_TRANSITIONS,
)
from app.db.session import get_db
from app.models.user import User
from app.repositories.admin_order_repository import (
    AdminOrderRepository,
)
from app.services.admin_order_service import (
    AdminOrderService,
)
from app.web.dependencies import (
    get_admin_web_user,
)
from app.web.templates import templates

from app.web.flash import flash

from app.web.export_utils import csv_response

# from fastapi.templating import (
#     Jinja2Templates,
# )
import urllib.request as urllib_request


# templates = Jinja2Templates(
#     directory="app/templates"
# )

from app.web.csrf import validate_csrf 

from fastapi import Request

router = APIRouter()


# ==========================================
# Order List
# ==========================================

@router.get("/orders")
async def order_list(
    request: Request,

    search: str | None = Query(
        default=None
    ),

    order_status: str | None = Query(
        default=None
    ),

    payment_status: str | None = Query(
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
        AdminOrderRepository(db)
    )

    orders, total = (
        await repository.list_orders(
            search=search,
            order_status=order_status,
            payment_status=payment_status,
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
        name="admin/orders/list.html",
        context={
            "admin": current_admin,

            "orders": orders,

            "search": (
                search or ""
            ),

            "selected_status": (
                order_status or ""
            ),

            "selected_payment": (
                payment_status or ""
            ),

            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (
                total_pages
            ),

            "active_page": "orders",
        },
    )


# ==========================================
# Order Detail
# ==========================================

# @router.get(
#     "/orders/{order_id}"
# )
# async def order_detail(
#     order_id: int,
#     request: Request,

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(get_db),
# ):

@router.get("/orders/{order_id}")
async def order_detail(
    
    request: Request,
    order_id: int,

    error: str | None = Query(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):
    repository = (
        AdminOrderRepository(db)
    )

    order = await repository.get_by_id(
        order_id
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    customer = (
        await repository.get_customer(
            order.user_id
        )
    )

    allowed_transitions = list(
        ORDER_TRANSITIONS.get(
            order.order_status,
            set(),
        )
    )

    # Keep UI ordering predictable

    status_order = [
        "CONFIRMED",
        "PROCESSING",
        "PACKED",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "CANCELLED",
        "DELIVERY_FAILED",
    ]

    allowed_transitions = [
        status
        for status in status_order
        if status in allowed_transitions
    ]

    return templates.TemplateResponse(
        request=request,
        name="admin/orders/detail.html",
        context={
            "admin": current_admin,
            "order": order,
            "customer": customer,

            "allowed_transitions": (
                allowed_transitions
            ),

            "active_page": "orders",

            "error": error,
        },
    )


# ==========================================
# Update Order Status
# ==========================================

@router.post(
    "/orders/{order_id}/status",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def update_order_status(
    
    request: Request,
    order_id: int,

    new_status: str = Form(...),

    note: str | None = Form(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = AdminOrderService(
        db
    )

    try:

        await service.update_status(
            order_id=order_id,
            new_status=new_status,
            admin_id=current_admin.id,
            note=note,
        )

    except HTTPException as exc:

        # Redirect with simple query error.
        # We can add flash messages later.
        flash(
    request,
    str(exc.detail),
    "danger",
)

        return RedirectResponse(
            url=(
                f"/admin/orders/"
                f"{order_id}"
                f"?error={exc.detail}"
            ),
            status_code=303,
        )
        
    flash(
    request,
    f"Order updated to {new_status.replace('_', ' ').title()} successfully.",
)

    return RedirectResponse(
        url=(
            f"/admin/orders/"
            f"{order_id}"
        ),
        status_code=303,
    )
    



@router.get("/orders/export.csv")
async def export_orders(
    current_admin: User = Depends(
        get_admin_web_user
    ),
    db: AsyncSession = Depends(get_db),
):

    orders, _ = await (
        AdminOrderRepository(db)
        .list_orders(
            page=1,
            limit=10000,
        )
    )

    return csv_response(
        filename="gramago_orders.csv",

        headers=[
            "Order Number",
            "Customer",
            "Phone",
            "Status",
            "Payment",
            "Total",
            "Created",
        ],

        rows=[
            [
                order.order_number,
                order.delivery_full_name,
                order.delivery_phone,
                order.order_status,
                order.payment_status,
                order.total_amount,
                order.created_at,
            ]
            for order in orders
        ],
    )
    
    


@router.get(
    "/orders/{order_id}/print"
)
async def print_order(
    order_id: int,
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = (
        AdminOrderRepository(db)
    )

    order = await repository.get_by_id(
        order_id
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/orders/print.html",
        context={
            "admin": current_admin,
            "order": order,
        },
    )