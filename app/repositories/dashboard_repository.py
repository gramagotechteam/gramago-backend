# from datetime import datetime, timezone

# from sqlalchemy import (
#     case,
#     func,
#     select,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.inventory import Inventory
# from app.models.order import Order
# from app.models.product import Product
# from app.models.user import User


# class DashboardRepository:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db
        
#         async def total_customers(self,):
            
            

#             result = await self.db.execute(
#                 select(
#                     func.count(User.id)
#                 )
#                 .where(
#                     User.role == "CUSTOMER"
#                 )
#             )

#             return result.scalar_one()
        
        
#         async def total_orders(self,):

#             result = await self.db.execute(
#                 select(
#                     func.count(Order.id)
#                 )
#             )

#             return result.scalar_one()
                
        
#         async def pending_orders(
#     self,
#         ):

#             result = await self.db.execute(
#                 select(
#                     func.count(Order.id)
#                 )
#                 .where(
#                     Order.order_status.in_(
#                         [
#                             "PLACED",
#                             "CONFIRMED",
#                             "PROCESSING",
#                             "PACKED",
#                             "OUT_FOR_DELIVERY",
#                         ]
#                     )
#                 )
#             )

#             return result.scalar_one()
        
        

#         async def delivered_orders(
#     self,
#         ):

#             result = await self.db.execute(
#                 select(
#                     func.count(Order.id)
#                 )
#                 .where(
#                     Order.order_status
#                     == "DELIVERED"
#                 )
#             )

#             return result.scalar_one()
        

#         async def delivered_orders(
#     self,
#         ):

#             result = await self.db.execute(
#                 select(
#                     func.count(Order.id)
#                 )
#                 .where(
#                     Order.order_status
#                     == "DELIVERED"
#                 )
#             )

#             return result.scalar_one()
        

        
#         async def active_products(
#     self,
#         ):

#             result = await self.db.execute(
#                 select(
#                     func.count(Product.id)
#                 )
#                 .where(
#                     Product.is_active
#                     .is_(True)
#                 )
#             )

#             return result.scalar_one()
        
        
        
#         async def low_stock_count(
#     self,
#         ):

#             result = await self.db.execute(
#                 select(
#                     func.count(
#                         Inventory.id
#                     )
#                 )
#                 .where(
#                     (
#                         Inventory.available_quantity
#                         - Inventory.reserved_quantity
#                     )
#                     <= Inventory.reorder_level
#                 )
#             )

#             return result.scalar_one()
        

#         async def low_stock_count(
#     self,
#         ):

#             result = await self.db.execute(
#                 select(
#                     func.count(
#                         Inventory.id
#                     )
#                 )
#                 .where(
#                     (
#                         Inventory.available_quantity
#                         - Inventory.reserved_quantity
#                     )
#                     <= Inventory.reorder_level
#                 )
#             )

#             return result.scalar_one()
        
        
#         async def today_revenue(
#     self,
#         ):

#             today = datetime.now(
#                 timezone.utc
#             ).date()

#             result = await self.db.execute(
#                 select(
#                     func.coalesce(
#                         func.sum(
#                             Order.total_amount
#                         ),
#                         0,
#                     )
#                 )
#                 .where(
#                     func.date(
#                         Order.created_at
#                     )
#                     == today,

#                     Order.payment_status
#                     == "PAID",
#                 )
#             )

#             return result.scalar_one()
        
        
        
        
#         async def recent_orders(
#     self,
#     limit: int = 10,
#         ):

#             result = await self.db.execute(
#                 select(Order)
#                 .order_by(
#                     Order.created_at.desc()
#                 )
#                 .limit(limit)
#             )

#             return result.scalars().all()
        
        
        
        


from datetime import datetime, timezone

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.models.order import Order
from app.models.product import Product
from app.models.user import User


class DashboardRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # --------------------------------------------------
    # Customers
    # --------------------------------------------------

    async def total_customers(
        self,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(User.id)
            )
            .where(
                User.role == "CUSTOMER"
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Total orders
    # --------------------------------------------------

    async def total_orders(
        self,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(Order.id)
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Pending orders
    # --------------------------------------------------

    async def pending_orders(
        self,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(Order.id)
            )
            .where(
                Order.order_status.in_(
                    [
                        "PLACED",
                        "CONFIRMED",
                        "PROCESSING",
                        "PACKED",
                        "OUT_FOR_DELIVERY",
                    ]
                )
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Delivered orders
    # --------------------------------------------------

    async def delivered_orders(
        self,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(Order.id)
            )
            .where(
                Order.order_status
                == "DELIVERED"
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Total paid revenue
    # --------------------------------------------------

    async def total_revenue(
        self,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(
                        Order.total_amount
                    ),
                    0,
                )
            )
            .where(
                Order.payment_status
                == "PAID"
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Active products
    # --------------------------------------------------

    async def active_products(
        self,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(Product.id)
            )
            .where(
                Product.is_active.is_(True)
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Low stock
    # --------------------------------------------------

    async def low_stock_count(
        self,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(
                    Inventory.id
                )
            )
            .where(
                (
                    Inventory.available_quantity
                    - Inventory.reserved_quantity
                )
                <= Inventory.reorder_level
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Today's orders
    # --------------------------------------------------

    async def today_orders(
        self,
    ) -> int:

        today = datetime.now(
            timezone.utc
        ).date()

        result = await self.db.execute(
            select(
                func.count(Order.id)
            )
            .where(
                func.date(
                    Order.created_at
                )
                == today
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Today's revenue
    # --------------------------------------------------

    async def today_revenue(
        self,
    ):

        today = datetime.now(
            timezone.utc
        ).date()

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(
                        Order.total_amount
                    ),
                    0,
                )
            )
            .where(
                func.date(
                    Order.created_at
                )
                == today,

                Order.payment_status
                == "PAID",
            )
        )

        return result.scalar_one()


    # --------------------------------------------------
    # Recent orders
    # --------------------------------------------------

    async def recent_orders(
        self,
        limit: int = 10,
    ):

        result = await self.db.execute(
            select(Order)
            .order_by(
                Order.created_at.desc()
            )
            .limit(limit)
        )

        return result.scalars().all()