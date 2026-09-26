# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload

# from app.models.order import Order


# class OrderRepository:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db


#     async def get_by_id(
#         self,
#         order_id: int,
#     ) -> Order | None:

#         result = await self.db.execute(
#             select(Order)
#             .where(
#                 Order.id == order_id
#             )
#             .options(
#                 selectinload(
#                     Order.items
#                 ),
#                 selectinload(
#                     Order.payment
#                 ),
#                 selectinload(
#                     Order.status_history
#                 ),
#             )
#         )

#         return result.scalar_one_or_none()


#     async def get_user_order(
#         self,
#         order_id: int,
#         user_id: int,
#     ) -> Order | None:

#         result = await self.db.execute(
#             select(Order)
#             .where(
#                 Order.id == order_id,
#                 Order.user_id == user_id,
#             )
#             .options(
#                 selectinload(
#                     Order.items
#                 ),
#                 selectinload(
#                     Order.payment
#                 ),
#                 selectinload(
#                     Order.status_history
#                 ),
#             )
#         )

#         return result.scalar_one_or_none()


#     async def list_user_orders(
#         self,
#         user_id: int,
#     ):

#         result = await self.db.execute(
#             select(Order)
#             .where(
#                 Order.user_id == user_id
#             )
#             .order_by(
#                 Order.created_at.desc()
#             )
#         )

#         return result.scalars().all()



from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy.orm import (
    selectinload,
)

from app.models.order import Order

from app.models.product_image import (
    ProductImage,
)


class OrderRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # =========================================
    # Attach Product Images To Order Items
    # =========================================

    async def _attach_item_images(
        self,
        order: Order | None,
    ) -> Order | None:

        if not order:
            return None


        if not order.items:
            return order


        # -------------------------------------
        # Collect product IDs
        # -------------------------------------

        product_ids = {
            item.product_id
            for item in order.items
            if item.product_id is not None
        }


        if not product_ids:
            return order


        # -------------------------------------
        # Fetch all product images
        # in ONE database query
        # -------------------------------------

        result = await self.db.execute(

            select(ProductImage)

            .where(
                ProductImage.product_id.in_(
                    product_ids
                )
            )

            .order_by(
                ProductImage.product_id,
                ProductImage.is_primary.desc(),
                ProductImage.id,
            )
        )


        images = (
            result.scalars().all()
        )


        # -------------------------------------
        # Build:
        #
        # product_id -> image_url
        #
        # Primary image will come first.
        # If no primary exists, first image
        # becomes fallback.
        # -------------------------------------

        image_map: dict[int, str] = {}


        for image in images:

            if (
                image.product_id
                not in image_map
            ):
                image_map[
                    image.product_id
                ] = image.image_url


        # -------------------------------------
        # Attach image_url dynamically
        # to each OrderItem ORM object
        # -------------------------------------

        for item in order.items:

            image_url = None


            if item.product_id is not None:

                image_url = image_map.get(
                    item.product_id
                )


            setattr(
                item,
                "image_url",
                image_url,
            )


        return order


    # =========================================
    # Admin / Internal Order Detail
    # =========================================

    async def get_by_id(
        self,
        order_id: int,
    ) -> Order | None:

        result = await self.db.execute(

            select(Order)

            .where(
                Order.id == order_id
            )

            .options(

                selectinload(
                    Order.items
                ),

                selectinload(
                    Order.payment
                ),

                selectinload(
                    Order.status_history
                ),
            )
        )


        order = (
            result.scalar_one_or_none()
        )


        return await self._attach_item_images(
            order
        )


    # =========================================
    # Customer Order Detail
    # =========================================

    async def get_user_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order | None:

        result = await self.db.execute(

            select(Order)

            .where(
                Order.id == order_id,

                Order.user_id == user_id,
            )

            .options(

                selectinload(
                    Order.items
                ),

                selectinload(
                    Order.payment
                ),

                selectinload(
                    Order.status_history
                ),
            )
        )


        order = (
            result.scalar_one_or_none()
        )


        return await self._attach_item_images(
            order
        )


    # =========================================
    # Customer Orders List
    # =========================================

    async def list_user_orders(
        self,
        user_id: int,
    ):

        result = await self.db.execute(

            select(Order)

            .where(
                Order.user_id == user_id
            )

            .order_by(
                Order.created_at.desc()
            )
        )


        return result.scalars().all()