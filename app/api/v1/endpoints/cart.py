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
from app.schemas.cart import (
    CartAddItemRequest,
    CartUpdateItemRequest,
)
from app.services.cart_service import (
    CartService,
)


router = APIRouter()


@router.get("")
async def get_cart(
    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CartService(db)

    cart = await service.get_cart(
        current_user.id
    )

    return {
        "success": True,
        "message": "Cart fetched successfully",
        "data": cart,
    }


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
)
async def add_cart_item(
    data: CartAddItemRequest,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CartService(db)

    await service.add_item(
        user_id=current_user.id,
        product_id=data.product_id,
        quantity=data.quantity,
    )

    cart = await service.get_cart(
        current_user.id
    )

    return {
        "success": True,
        "message": "Product added to cart",
        "data": cart,
    }


@router.patch("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    data: CartUpdateItemRequest,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CartService(db)

    await service.update_item(
        user_id=current_user.id,
        item_id=item_id,
        quantity=data.quantity,
    )

    cart = await service.get_cart(
        current_user.id
    )

    return {
        "success": True,
        "message": "Cart updated successfully",
        "data": cart,
    }


@router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CartService(db)

    await service.remove_item(
        user_id=current_user.id,
        item_id=item_id,
    )

    cart = await service.get_cart(
        current_user.id
    )

    return {
        "success": True,
        "message": "Product removed from cart",
        "data": cart,
    }


@router.delete("")
async def clear_cart(
    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = CartService(db)

    await service.clear_cart(
        current_user.id
    )

    return {
        "success": True,
        "message": "Cart cleared successfully",
        "data": {
            "items": [],
            "item_count": 0,
            "subtotal": 0,
        },
    }