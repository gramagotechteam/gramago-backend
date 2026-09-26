from decimal import Decimal

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart_item import CartItem
from app.repositories.cart_repository import (
    CartRepository,
)
from app.repositories.product_repository import (
    ProductRepository,
)


class CartService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.carts = CartRepository(db)
        self.products = ProductRepository(db)


    def _effective_price(
        self,
        product,
    ) -> Decimal:

        if product.discount_price is not None:

            return product.discount_price

        return product.price


    def _validate_quantity(
        self,
        product,
        quantity: Decimal,
    ):

        if quantity < product.min_order_qty:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Minimum order quantity is "
                    f"{product.min_order_qty}"
                ),
            )

        if (
            product.max_order_qty is not None
            and quantity
            > product.max_order_qty
        ):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Maximum order quantity is "
                    f"{product.max_order_qty}"
                ),
            )


    async def _validate_stock(
        self,
        product,
        quantity: Decimal,
    ):

        if not product.inventory:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product inventory unavailable",
            )

        sellable = (
            product.inventory.available_quantity
            - product.inventory.reserved_quantity
        )

        if quantity > sellable:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Only {sellable} quantity "
                    f"is currently available"
                ),
            )


    async def add_item(
        self,
        user_id: int,
        product_id: int,
        quantity: Decimal,
    ):

        product = await self.products.get_by_id(
            product_id,
            include_relations=True,
        )

        if not product or not product.is_active:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        self._validate_quantity(
            product,
            quantity,
        )

        await self._validate_stock(
            product,
            quantity,
        )

        cart = await self.carts.get_or_create_cart(
            user_id
        )

        existing = await self.carts.get_item(
            cart.id,
            product_id,
        )

        if existing:

            new_quantity = (
                existing.quantity
                + quantity
            )

            self._validate_quantity(
                product,
                new_quantity,
            )

            await self._validate_stock(
                product,
                new_quantity,
            )

            existing.quantity = (
                new_quantity
            )

        else:

            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
            )

            self.db.add(item)

        await self.db.commit()


    async def update_item(
        self,
        user_id: int,
        item_id: int,
        quantity: Decimal,
    ):

        cart = await self.carts.get_active_cart(
            user_id
        )

        if not cart:

            raise HTTPException(
                status_code=404,
                detail="Cart not found",
            )

        item = await self.carts.get_item_by_id(
            cart.id,
            item_id,
        )

        if not item:

            raise HTTPException(
                status_code=404,
                detail="Cart item not found",
            )

        product = await self.products.get_by_id(
            item.product_id,
            include_relations=True,
        )

        if not product or not product.is_active:

            raise HTTPException(
                status_code=400,
                detail="Product is unavailable",
            )

        self._validate_quantity(
            product,
            quantity,
        )

        await self._validate_stock(
            product,
            quantity,
        )

        item.quantity = quantity

        await self.db.commit()


    async def remove_item(
        self,
        user_id: int,
        item_id: int,
    ):

        cart = await self.carts.get_active_cart(
            user_id
        )

        if not cart:

            raise HTTPException(
                status_code=404,
                detail="Cart not found",
            )

        item = await self.carts.get_item_by_id(
            cart.id,
            item_id,
        )

        if not item:

            raise HTTPException(
                status_code=404,
                detail="Cart item not found",
            )

        await self.db.delete(item)

        await self.db.commit()


    async def clear_cart(
        self,
        user_id: int,
    ):

        cart = await self.carts.get_active_cart(
            user_id,
            include_items=True,
        )

        if not cart:
            return

        for item in list(cart.items):
            await self.db.delete(item)

        await self.db.commit()
        
        
        
        
    async def get_cart(
        self,
        user_id: int,
    ):

        cart = await self.carts.get_active_cart(
            user_id,
            include_items=True,
        )

        if not cart:

            return {
                "id": None,
                "items": [],
                "item_count": 0,
                "subtotal": Decimal("0.00"),
            }

        items_data = []

        subtotal = Decimal("0.00")

        for item in cart.items:

            product = item.product

            if not product:
                continue

            price = self._effective_price(
                product
            )

            line_total = (
                price
                * item.quantity
            )

            subtotal += line_total

            primary_image = None

            for image in product.images:

                if image.is_primary:
                    primary_image = (
                        image.image_url
                    )
                    break

            if (
                not primary_image
                and product.images
            ):
                primary_image = (
                    product.images[0].image_url
                )

            sellable_quantity = Decimal(
                "0"
            )

            if product.inventory:

                sellable_quantity = (
                    product.inventory.available_quantity
                    - product.inventory.reserved_quantity
                )

            items_data.append(
                {
                    "id": item.id,

                    "product_id": product.id,

                    "name": product.name,

                    "image_url": primary_image,

                    "quantity": item.quantity,

                    "unit": product.unit,

                    "unit_value": (
                        product.unit_value
                    ),

                    "price": product.price,

                    "discount_price": (
                        product.discount_price
                    ),

                    "effective_price": price,

                    "line_total": line_total,

                    "available_quantity": (
                        sellable_quantity
                    ),

                    "is_available": (
                        product.is_active
                        and sellable_quantity
                        >= item.quantity
                    ),
                }
            )

        return {
            "id": cart.id,
            "items": items_data,
            "item_count": len(items_data),
            "subtotal": subtotal,
        }
        
        
    