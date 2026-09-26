from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product


class CartRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    async def get_active_cart(
        self,
        user_id: int,
        include_items: bool = False,
    ) -> Cart | None:

        stmt = select(Cart).where(
            Cart.user_id == user_id,
            Cart.status == "ACTIVE",
        )

        if include_items:

            stmt = stmt.options(
                selectinload(
                    Cart.items
                )
                .selectinload(
                    CartItem.product
                )
                .selectinload(
                    Product.images
                ),

                selectinload(
                    Cart.items
                )
                .selectinload(
                    CartItem.product
                )
                .selectinload(
                    Product.inventory
                ),
            )

        result = await self.db.execute(
            stmt
        )

        return result.scalar_one_or_none()


    async def get_or_create_cart(
        self,
        user_id: int,
    ) -> Cart:

        cart = await self.get_active_cart(
            user_id
        )

        if cart:
            return cart

        cart = Cart(
            user_id=user_id,
            status="ACTIVE",
        )

        self.db.add(cart)

        await self.db.flush()

        return cart


    async def get_item(
        self,
        cart_id: int,
        product_id: int,
    ) -> CartItem | None:

        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id
                == product_id,
            )
        )

        return result.scalar_one_or_none()


    async def get_item_by_id(
        self,
        cart_id: int,
        item_id: int,
    ) -> CartItem | None:

        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.id == item_id,
            )
        )

        return result.scalar_one_or_none()