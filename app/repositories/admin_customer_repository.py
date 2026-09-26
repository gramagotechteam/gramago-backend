from sqlalchemy import (
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.user import User
from app.models.user_address import UserAddress


class AdminCustomerRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # ==========================================
    # Customer List
    # ==========================================

    async def list_customers(
        self,
        *,
        search: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        limit: int = 20,
    ):

        conditions = [
            User.role == "CUSTOMER"
        ]

        if search:

            keyword = (
                f"%{search.strip()}%"
            )

            conditions.append(
                or_(
                    User.full_name.ilike(
                        keyword
                    ),
                    User.email.ilike(
                        keyword
                    ),
                    User.phone.ilike(
                        keyword
                    ),
                )
            )

        if is_active is not None:

            conditions.append(
                User.is_active
                == is_active
            )


        count_result = await self.db.execute(
            select(
                func.count(User.id)
            )
            .where(
                *conditions
            )
        )

        total = count_result.scalar_one()


        result = await self.db.execute(
            select(User)
            .where(
                *conditions
            )
            .order_by(
                User.created_at.desc()
            )
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
        )

        customers = (
            result.scalars().all()
        )

        return customers, total


    # ==========================================
    # Customer Detail
    # ==========================================

    async def get_customer(
        self,
        user_id: int,
    ) -> User | None:

        result = await self.db.execute(
            select(User)
            .where(
                User.id == user_id,
                User.role == "CUSTOMER",
            )
        )

        return result.scalar_one_or_none()


    # ==========================================
    # Addresses
    # ==========================================

    async def get_addresses(
        self,
        user_id: int,
    ):

        result = await self.db.execute(
            select(UserAddress)
            .where(
                UserAddress.user_id
                == user_id
            )
            .order_by(
                UserAddress.is_default.desc(),
                UserAddress.created_at.desc(),
            )
        )

        return result.scalars().all()


    # ==========================================
    # Customer Orders
    # ==========================================

    async def get_orders(
        self,
        user_id: int,
        limit: int = 50,
    ):

        result = await self.db.execute(
            select(Order)
            .where(
                Order.user_id
                == user_id
            )
            .order_by(
                Order.created_at.desc()
            )
            .limit(limit)
        )

        return result.scalars().all()


    # ==========================================
    # Statistics
    # ==========================================

    async def get_stats(
        self,
        user_id: int,
    ):

        result = await self.db.execute(
            select(

                func.count(
                    Order.id
                ).label(
                    "total_orders"
                ),

                func.count(
                    Order.id
                )
                .filter(
                    Order.order_status
                    == "DELIVERED"
                )
                .label(
                    "delivered_orders"
                ),

                func.count(
                    Order.id
                )
                .filter(
                    Order.order_status
                    == "CANCELLED"
                )
                .label(
                    "cancelled_orders"
                ),

                func.coalesce(
                    func.sum(
                        Order.total_amount
                    )
                    .filter(
                        Order.payment_status
                        == "PAID"
                    ),
                    0,
                )
                .label(
                    "total_spent"
                ),
            )
            .where(
                Order.user_id
                == user_id
            )
        )

        row = result.one()

        return {
            "total_orders":
                row.total_orders,

            "delivered_orders":
                row.delivered_orders,

            "cancelled_orders":
                row.cancelled_orders,

            "total_spent":
                row.total_spent,
        }