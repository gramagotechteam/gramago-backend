# # from sqlalchemy import (
# #     desc,
# #     func,
# #     select,
# # )
# # from sqlalchemy.ext.asyncio import AsyncSession

# # from app.models.order import Order
# # from app.models.order_item import OrderItem


# # class ReportRepository:

# #     def __init__(
# #         self,
# #         db: AsyncSession,
# #     ):
# #         self.db = db
        
        
# #         async def order_status_summary(
# #     self,
# # ):

# #             result = await self.db.execute(
# #                 select(
# #                     Order.order_status,
# #                     func.count(
# #                         Order.id
# #                     ).label(
# #                         "count"
# #                     ),
# #                 )
# #                 .group_by(
# #                     Order.order_status
# #                 )
# #                 .order_by(
# #                     Order.order_status
# #                 )
# #             )

# #             return result.all()
        
        
        
# #         async def payment_status_summary(
# #     self,
# # ):

# #             result = await self.db.execute(
# #                 select(
# #                     Order.payment_status,

# #                     func.count(
# #                         Order.id
# #                     ).label(
# #                         "count"
# #                     ),
# #                 )
# #                 .group_by(
# #                     Order.payment_status
# #                 )
# #                 .order_by(
# #                     Order.payment_status
# #                 )
# #             )

# #             return result.all()
        
        
        
# #         async def top_products(
# #     self,
# #     limit: int = 10,
# #         ):

# #             result = await self.db.execute(
# #                 select(

# #                     OrderItem.product_id,

# #                     OrderItem.product_name,

# #                     func.sum(
# #                         OrderItem.quantity
# #                     ).label(
# #                         "quantity_sold"
# #                     ),

# #                     func.sum(
# #                         OrderItem.line_total
# #                     ).label(
# #                         "revenue"
# #                     ),
# #                 )
# #                 .join(
# #                     Order,
# #                     Order.id
# #                     == OrderItem.order_id,
# #                 )
# #                 .where(
# #                     Order.order_status
# #                     == "DELIVERED"
# #                 )
# #                 .group_by(
# #                     OrderItem.product_id,
# #                     OrderItem.product_name,
# #                 )
# #                 .order_by(
# #                     desc(
# #                         "quantity_sold"
# #                     )
# #                 )
# #                 .limit(limit)
# #             )

# #             return result.all()
        
        
        
# #         async def daily_sales(
# #     self,
# #         ):

# #             result = await self.db.execute(
# #                 select(

# #                     func.date(
# #                         Order.delivered_at
# #                     ).label(
# #                         "date"
# #                     ),

# #                     func.count(
# #                         Order.id
# #                     ).label(
# #                         "orders"
# #                     ),

# #                     func.sum(
# #                         Order.total_amount
# #                     ).label(
# #                         "revenue"
# #                     ),
# #                 )
# #                 .where(
# #                     Order.order_status
# #                     == "DELIVERED"
# #                 )
# #                 .group_by(
# #                     func.date(
# #                         Order.delivered_at
# #                     )
# #                 )
# #                 .order_by(
# #                     func.date(
# #                         Order.delivered_at
# #                     ).desc()
# #                 )
# #                 .limit(30)
# #             )

# #             return result.all()
        
        
        


# from sqlalchemy import (
#     desc,
#     func,
#     select,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.order import Order
# from app.models.order_item import OrderItem


# class ReportRepository:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db


#     # --------------------------------------------------
#     # Order Status Summary
#     # --------------------------------------------------

#     async def order_status_summary(
#         self,
#     ):

#         result = await self.db.execute(
#             select(
#                 Order.order_status,

#                 func.count(
#                     Order.id
#                 ).label(
#                     "count"
#                 ),
#             )
#             .group_by(
#                 Order.order_status
#             )
#             .order_by(
#                 Order.order_status
#             )
#         )

#         return result.all()


#     # --------------------------------------------------
#     # Payment Status Summary
#     # --------------------------------------------------

#     async def payment_status_summary(
#         self,
#     ):

#         result = await self.db.execute(
#             select(
#                 Order.payment_status,

#                 func.count(
#                     Order.id
#                 ).label(
#                     "count"
#                 ),
#             )
#             .group_by(
#                 Order.payment_status
#             )
#             .order_by(
#                 Order.payment_status
#             )
#         )

#         return result.all()


#     # --------------------------------------------------
#     # Top Products
#     # --------------------------------------------------

#     async def top_products(
#         self,
#         limit: int = 10,
#     ):

#         quantity_sold = func.sum(
#             OrderItem.quantity
#         ).label(
#             "quantity_sold"
#         )

#         revenue = func.sum(
#             OrderItem.line_total
#         ).label(
#             "revenue"
#         )

#         result = await self.db.execute(
#             select(
#                 OrderItem.product_id,
#                 OrderItem.product_name,
#                 quantity_sold,
#                 revenue,
#             )
#             .join(
#                 Order,
#                 Order.id
#                 == OrderItem.order_id,
#             )
#             .where(
#                 Order.order_status
#                 == "DELIVERED"
#             )
#             .group_by(
#                 OrderItem.product_id,
#                 OrderItem.product_name,
#             )
#             .order_by(
#                 quantity_sold.desc()
#             )
#             .limit(limit)
#         )

#         return result.all()


#     # --------------------------------------------------
#     # Daily Sales
#     # --------------------------------------------------

#     async def daily_sales(
#         self,
#         limit: int = 30,
#     ):

#         sale_date = func.date(
#             Order.delivered_at
#         ).label(
#             "sale_date"
#         )

#         order_count = func.count(
#             Order.id
#         ).label(
#             "orders"
#         )

#         revenue = func.sum(
#             Order.total_amount
#         ).label(
#             "revenue"
#         )

#         result = await self.db.execute(
#             select(
#                 sale_date,
#                 order_count,
#                 revenue,
#             )
#             .where(
#                 Order.order_status
#                 == "DELIVERED",

#                 Order.payment_status
#                 == "PAID",

#                 Order.delivered_at.is_not(
#                     None
#                 ),
#             )
#             .group_by(
#                 func.date(
#                     Order.delivered_at
#                 )
#             )
#             .order_by(
#                 func.date(
#                     Order.delivered_at
#                 ).desc()
#             )
#             .limit(limit)
#         )

#         return result.all()



from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    desc,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem


class ReportRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # ==========================================
    # Order Status Summary
    # ==========================================

    async def order_status_summary(
        self,
    ):

        result = await self.db.execute(
            select(
                Order.order_status,

                func.count(
                    Order.id
                ).label(
                    "count"
                ),
            )
            .group_by(
                Order.order_status
            )
            .order_by(
                Order.order_status
            )
        )

        return result.all()


    # ==========================================
    # Payment Status Summary
    # ==========================================

    async def payment_status_summary(
        self,
    ):

        result = await self.db.execute(
            select(
                Order.payment_status,

                func.count(
                    Order.id
                ).label(
                    "count"
                ),
            )
            .group_by(
                Order.payment_status
            )
            .order_by(
                Order.payment_status
            )
        )

        return result.all()


    # ==========================================
    # Top Products
    # ==========================================

    async def top_products(
        self,
        limit: int = 10,
    ):

        quantity_sold = func.sum(
            OrderItem.quantity
        ).label(
            "quantity_sold"
        )

        revenue = func.sum(
            OrderItem.line_total
        ).label(
            "revenue"
        )

        result = await self.db.execute(
            select(
                OrderItem.product_id,
                OrderItem.product_name,
                quantity_sold,
                revenue,
            )
            .join(
                Order,
                Order.id
                == OrderItem.order_id,
            )
            .where(
                Order.order_status
                == "DELIVERED",

                Order.payment_status
                == "PAID",
            )
            .group_by(
                OrderItem.product_id,
                OrderItem.product_name,
            )
            .order_by(
                quantity_sold.desc()
            )
            .limit(limit)
        )

        return result.all()


    # ==========================================
    # Daily Sales
    # ==========================================

    async def daily_sales(
        self,
        days: int = 30,
    ):

        start_date = (
            datetime.now(
                timezone.utc
            )
            - timedelta(
                days=days - 1
            )
        ).date()

        sale_date = func.date(
            Order.delivered_at
        ).label(
            "sale_date"
        )

        order_count = func.count(
            Order.id
        ).label(
            "orders"
        )

        revenue = func.coalesce(
            func.sum(
                Order.total_amount
            ),
            0,
        ).label(
            "revenue"
        )

        result = await self.db.execute(
            select(
                sale_date,
                order_count,
                revenue,
            )
            .where(
                Order.order_status
                == "DELIVERED",

                Order.payment_status
                == "PAID",

                Order.delivered_at
                .is_not(None),

                func.date(
                    Order.delivered_at
                )
                >= start_date,
            )
            .group_by(
                func.date(
                    Order.delivered_at
                )
            )
            .order_by(
                func.date(
                    Order.delivered_at
                )
            )
        )

        return result.all()


    # ==========================================
    # Report KPI Summary
    # ==========================================

    async def report_summary(
        self,
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

                func.count(
                    Order.id
                )
                .filter(
                    Order.order_status
                    == "DELIVERY_FAILED"
                )
                .label(
                    "failed_orders"
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
                    "total_revenue"
                ),
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

            "failed_orders":
                row.failed_orders,

            "total_revenue":
                row.total_revenue,
        }


    # ==========================================
    # Today's Revenue
    # ==========================================

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
                Order.payment_status
                == "PAID",

                func.date(
                    Order.delivered_at
                )
                == today,
            )
        )

        return result.scalar_one()


    # ==========================================
    # Today's Delivered Orders
    # ==========================================

    async def today_orders(
        self,
    ):

        today = datetime.now(
            timezone.utc
        ).date()

        result = await self.db.execute(
            select(
                func.count(
                    Order.id
                )
            )
            .where(
                Order.order_status
                == "DELIVERED",

                func.date(
                    Order.delivered_at
                )
                == today,
            )
        )

        return result.scalar_one()
    
    
    
    async def average_order_value(
    self,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.avg(
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