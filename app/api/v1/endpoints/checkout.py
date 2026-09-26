from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User
from app.schemas.order import (
    CheckoutRequest,
)
from app.services.checkout_service import (
    CheckoutService,
)


router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def checkout(
    data: CheckoutRequest,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CheckoutService(db)

    order = await service.create_order(
        user_id=current_user.id,
        address_id=data.address_id,
        customer_note=data.customer_note,
    )

    return {
        "success": True,
        "message": "Order placed successfully",
        "data": {
            "id": order.id,

            "order_number": (
                order.order_number
            ),

            "order_status": (
                order.order_status
            ),

            "payment_method": "COD",

            "payment_status": (
                order.payment_status
            ),

            "subtotal": order.subtotal,

            "delivery_fee": (
                order.delivery_fee
            ),

            "total_amount": (
                order.total_amount
            ),
        },
    }