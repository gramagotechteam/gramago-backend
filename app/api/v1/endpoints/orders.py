from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User
from app.repositories.order_repository import (
    OrderRepository,
)
from app.schemas.order import (
    OrderDetailResponse,
    OrderListResponse,
)


router = APIRouter()


@router.get("")
async def list_orders(
    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = OrderRepository(db)

    orders = await repository.list_user_orders(
        current_user.id
    )

    return {
        "success": True,
        "message": "Orders fetched successfully",
        "data": [
            OrderListResponse.model_validate(
                order
            )
            for order in orders
        ],
    }


@router.get("/{order_id}")
async def get_order(
    order_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = OrderRepository(db)

    order = await repository.get_user_order(
        order_id,
        current_user.id,
    )

    if not order:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return {
        "success": True,
        "message": "Order fetched successfully",
        "data": (
            OrderDetailResponse
            .model_validate(order)
        ),
    }
    
    


from app.services.order_service import (
    OrderService,
)


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = OrderService(db)

    await service.cancel_customer_order(
        order_id=order_id,
        user_id=current_user.id,
    )

    return {
        "success": True,
        "message": "Order cancelled successfully",
        "data": None,
    }