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
from app.dependencies.auth import (
    require_admin,
)
from app.models.user import User
from app.repositories.admin_order_repository import (
    AdminOrderRepository,
)
from app.schemas.order import (
    AdminOrderDetailResponse,
    AdminOrderListResponse,
    OrderStatusUpdate,
)
from app.services.admin_order_service import (
    AdminOrderService,
)


router = APIRouter()




@router.get("")
async def list_orders(
    order_status: str | None = None,

    payment_status: str | None = None,

    search: str | None = Query(
        default=None,
        max_length=100,
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

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = (
        AdminOrderRepository(db)
    )


    orders, total = (
        await repository.list_orders(

            order_status=(
                order_status
            ),

            payment_status=(
                payment_status
            ),

            search=search,

            page=page,

            limit=limit,
        )
    )


    total_pages = (
        ceil(total / limit)
        if total
        else 0
    )


    return {

        "success": True,

        "message": (
            "Orders fetched successfully"
        ),

        "data": [

            AdminOrderListResponse
            .model_validate(order)

            for order in orders
        ],

        "pagination": {

            "page": page,

            "limit": limit,

            "total_items": total,

            "total_pages": (
                total_pages
            ),
        },
    }
    
    




@router.get("/{order_id}")
async def get_order(
    order_id: int,

    current_user: User = Depends(
        require_admin
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
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Order not found",
        )


    return {

        "success": True,

        "message": (
            "Order fetched successfully"
        ),

        "data": (
            AdminOrderDetailResponse
            .model_validate(order)
        ),
    }
    
    
    
    



@router.patch(
    "/{order_id}/status"
)
async def update_order_status(
    order_id: int,

    data: OrderStatusUpdate,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    service = (
        AdminOrderService(db)
    )


    order = await service.update_status(

        order_id=order_id,

        new_status=data.status,

        admin_id=current_user.id,

        note=data.note,
    )


    return {

        "success": True,

        "message": (
            f"Order status updated "
            f"to {order.order_status}"
        ),

        "data": {

            "id": order.id,

            "order_number": (
                order.order_number
            ),

            "order_status": (
                order.order_status
            ),

            "payment_status": (
                order.payment_status
            ),
        },
    }
    


