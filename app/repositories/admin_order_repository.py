# from sqlalchemy import (
#     func,
#     select,
# )
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload

# from app.models.order import Order


# class AdminOrderRepository:

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


#     async def list_orders(
#         self,
#         *,
#         order_status: str | None,
#         payment_status: str | None,
#         search: str | None,
#         page: int,
#         limit: int,
#     ):

#         conditions = []

#         if order_status:

#             conditions.append(
#                 Order.order_status
#                 == order_status
#             )

#         if payment_status:

#             conditions.append(
#                 Order.payment_status
#                 == payment_status
#             )

#         if search:

#             keyword = (
#                 f"%{search.strip()}%"
#             )

#             conditions.append(
#                 Order.order_number.ilike(
#                     keyword
#                 )
#             )


#         count_result = await self.db.execute(
#             select(
#                 func.count(Order.id)
#             )
#             .where(
#                 *conditions
#             )
#         )

#         total = (
#             count_result.scalar_one()
#         )


#         offset = (
#             page - 1
#         ) * limit


#         result = await self.db.execute(
#             select(Order)
#             .where(
#                 *conditions
#             )
#             .order_by(
#                 Order.created_at.desc()
#             )
#             .offset(offset)
#             .limit(limit)
#         )

#         orders = (
#             result.scalars().all()
#         )

#         return orders, total






from sqlalchemy import (
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.user import User


class AdminOrderRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # ==========================================
    # Order Detail
    # ==========================================

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

        return result.scalar_one_or_none()


    # ==========================================
    # Customer
    # ==========================================

    async def get_customer(
        self,
        user_id: int,
    ) -> User | None:

        result = await self.db.execute(
            select(User)
            .where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()


    # ==========================================
    # List / Search / Filter
    # ==========================================

    async def list_orders(
        self,
        *,
        order_status: str | None = None,
        payment_status: str | None = None,
        search: str | None = None,
        page: int = 1,
        limit: int = 20,
    ):

        conditions = []

        if order_status:

            conditions.append(
                Order.order_status
                == order_status
            )

        if payment_status:

            conditions.append(
                Order.payment_status
                == payment_status
            )

        if search:

            keyword = (
                f"%{search.strip()}%"
            )

            conditions.append(
                or_(
                    Order.order_number.ilike(
                        keyword
                    ),
                    Order.delivery_full_name.ilike(
                        keyword
                    ),
                    Order.delivery_phone.ilike(
                        keyword
                    ),
                )
            )


        count_result = await self.db.execute(
            select(
                func.count(Order.id)
            )
            .where(
                *conditions
            )
        )

        total = count_result.scalar_one()


        result = await self.db.execute(
            select(Order)
            .where(
                *conditions
            )
            .order_by(
                Order.created_at.desc()
            )
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
        )

        orders = (
            result.scalars().all()
        )

        return orders, total