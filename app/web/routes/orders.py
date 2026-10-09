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

    # allowed_transitions = list(
    #     ORDER_TRANSITIONS.get(
    #         order.order_status,
    #         set(),
    #     )
    # )
    
    


    # =========================================================
    # ADMIN MAY CONTROL ORDER ONLY UNTIL PACKED
    # =========================================================

    ADMIN_PREPARATION_TRANSITIONS = {

        "PLACED": [
            "CONFIRMED",
        ],

        "CONFIRMED": [
            "PROCESSING",
        ],

        "PROCESSING": [
            "PACKED",
        ],
    }


    allowed_transitions = (
        ADMIN_PREPARATION_TRANSITIONS.get(
            order.order_status,
            []
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
# Bulk Advance Orders
# ==========================================

@router.post(
    "/orders/bulk-advance",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def bulk_advance_orders(
    request: Request,

    order_ids: list[int] = Form(
        default=[]
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    if not order_ids:

        flash(
            request,
            "Please select at least one order.",
            "warning",
        )

        return RedirectResponse(
            url="/admin/orders",
            status_code=303,
        )

    service = AdminOrderService(
        db
    )

    # Admin can advance only through these states.
    next_status_map = {
        "PLACED": "CONFIRMED",
        "CONFIRMED": "PROCESSING",
        "PROCESSING": "PACKED",
    }

    updated_count = 0
    skipped_count = 0
    failed_count = 0

    for order_id in order_ids:

        repository = AdminOrderRepository(
            db
        )

        order = (
            await repository.get_by_id(
                order_id
            )
        )

        if order is None:
            failed_count += 1
            continue

        new_status = next_status_map.get(
            order.order_status
        )

        # PACKED and delivery-controlled
        # statuses are never changed here.
        if new_status is None:
            skipped_count += 1
            continue

        try:

            await service.update_status(
                order_id=order.id,
                new_status=new_status,
                admin_id=current_admin.id,
                note=(
                    "Bulk status update "
                    "from Admin Orders page"
                ),
            )

            updated_count += 1

        except HTTPException:

            failed_count += 1

    if updated_count > 0:

        message = (
            f"{updated_count} order"
            f"{'s' if updated_count != 1 else ''} "
            f"advanced successfully."
        )

        if skipped_count:

            message += (
                f" {skipped_count} already packed "
                f"or delivery-controlled "
                f"order"
                f"{'s were' if skipped_count != 1 else ' was'} "
                f"skipped."
            )

        if failed_count:

            message += (
                f" {failed_count} order"
                f"{'s' if failed_count != 1 else ''} "
                f"could not be updated."
            )

        flash(
            request,
            message,
            "success",
        )

    else:

        flash(
            request,
            (
                "No selected orders were eligible "
                "for an admin status update."
            ),
            "warning",
        )

    return RedirectResponse(
        url="/admin/orders",
        status_code=303,
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