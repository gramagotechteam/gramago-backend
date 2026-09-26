# from sqlalchemy.ext.asyncio import AsyncSession

# from app.repositories.dashboard_repository import (
#     DashboardRepository,
# )


# class DashboardService:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.repo = DashboardRepository(db)


#     async def get_summary(
#         self,
#     ):

#         return {

#             "customers": {
#                 "total": (
#                     await self.repo
#                     .total_customers()
#                 ),
#             },

#             "orders": {

#                 "total": (
#                     await self.repo
#                     .total_orders()
#                 ),

#                 "today": (
#                     await self.repo
#                     .today_orders()
#                 ),

#                 "pending": (
#                     await self.repo
#                     .pending_orders()
#                 ),

#                 "delivered": (
#                     await self.repo
#                     .delivered_orders()
#                 ),
#             },

#             "revenue": {

#                 "total": (
#                     await self.repo
#                     .total_revenue()
#                 ),

#                 "today": (
#                     await self.repo
#                     .today_revenue()
#                 ),
#             },

#             "catalog": {

#                 "active_products": (
#                     await self.repo
#                     .active_products()
#                 ),

#                 "low_stock": (
#                     await self.repo
#                     .low_stock_count()
#                 ),
#             },
#         }



from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard_repository import (
    DashboardRepository,
)


class DashboardService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.repo = DashboardRepository(
            db
        )


    async def get_summary(
        self,
    ):

        return {
            "customers": {
                "total": (
                    await self.repo
                    .total_customers()
                ),
            },

            "orders": {
                "total": (
                    await self.repo
                    .total_orders()
                ),

                "today": (
                    await self.repo
                    .today_orders()
                ),

                "pending": (
                    await self.repo
                    .pending_orders()
                ),

                "delivered": (
                    await self.repo
                    .delivered_orders()
                ),
            },

            "revenue": {
                "total": (
                    await self.repo
                    .total_revenue()
                ),

                "today": (
                    await self.repo
                    .today_revenue()
                ),
            },

            "catalog": {
                "active_products": (
                    await self.repo
                    .active_products()
                ),

                "low_stock": (
                    await self.repo
                    .low_stock_count()
                ),
            },
        }