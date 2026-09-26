# from fastapi import (
#     APIRouter,
#     Depends,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db
# from app.dependencies.auth import (
#     require_admin,
# )
# from app.models.user import User
# from app.repositories.report_repository import (
#     ReportRepository,
# )


# router = APIRouter()


# @router.get("/orders/status-summary")
# async def order_status_report(
#     current_user: User = Depends(
#         require_admin
#     ),

#     db: AsyncSession = Depends(get_db),
# ):

#     repo = ReportRepository(db)

#     rows = await repo.order_status_summary()

#     return {
#         "success": True,
#         "message": (
#             "Order status report fetched"
#         ),
#         "data": [
#             {
#                 "status": status,
#                 "count": count,
#             }
#             for status, count in rows
#         ],
#     }
    



# @router.get("/payments/status-summary")
# async def payment_status_report(
#     current_user: User = Depends(
#         require_admin
#     ),

#     db: AsyncSession = Depends(get_db),
# ):

#     repo = ReportRepository(db)

#     rows = await repo.payment_status_summary()

#     return {
#         "success": True,
#         "message": (
#             "Payment status report fetched"
#         ),
#         "data": [
#             {
#                 "status": payment_status,
#                 "count": count,
#             }
#             for payment_status, count in rows
#         ],
#     }
    
    


# @router.get("/products/top")
# async def top_products(
#     current_user: User = Depends(
#         require_admin
#     ),

#     db: AsyncSession = Depends(get_db),
# ):

#     repo = ReportRepository(db)

#     rows = await repo.top_products(
#         10
#     )

#     return {
#         "success": True,
#         "message": (
#             "Top products fetched"
#         ),
#         "data": [
#             {
#                 "product_id": product_id,
#                 "product_name": product_name,
#                 "quantity_sold": quantity_sold,
#                 "revenue": revenue,
#             }
#             for (
#                 product_id,
#                 product_name,
#                 quantity_sold,
#                 revenue,
#             ) in rows
#         ],
#     }
    
    
    



# @router.get("/sales/daily")
# async def daily_sales(
#     current_user: User = Depends(
#         require_admin
#     ),

#     db: AsyncSession = Depends(get_db),
# ):

#     repo = ReportRepository(db)

#     rows = await repo.daily_sales()

#     return {
#         "success": True,
#         "message": (
#             "Daily sales fetched"
#         ),
#         "data": [
#             {
#                 "date": date,
#                 "orders": orders,
#                 "revenue": revenue,
#             }
#             for (
#                 date,
#                 orders,
#                 revenue,
#             ) in rows
#         ],
#     }
    
    


from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.repositories.report_repository import (
    ReportRepository,
)


router = APIRouter()


# --------------------------------------------------
# Order status report
# --------------------------------------------------

@router.get("/orders/status-summary")
async def order_status_report(
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(db)

    rows = await repo.order_status_summary()

    return {
        "success": True,
        "message": "Order status report fetched successfully",
        "data": [
            {
                "status": order_status,
                "count": count,
            }
            for (
                order_status,
                count,
            ) in rows
        ],
    }


# --------------------------------------------------
# Payment status report
# --------------------------------------------------

@router.get("/payments/status-summary")
async def payment_status_report(
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(db)

    rows = (
        await repo.payment_status_summary()
    )

    return {
        "success": True,
        "message": "Payment status report fetched successfully",
        "data": [
            {
                "status": payment_status,
                "count": count,
            }
            for (
                payment_status,
                count,
            ) in rows
        ],
    }


# --------------------------------------------------
# Top products
# --------------------------------------------------

@router.get("/products/top")
async def top_products(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(db)

    rows = await repo.top_products(
        limit=limit
    )

    return {
        "success": True,
        "message": "Top products fetched successfully",
        "data": [
            {
                "product_id": product_id,
                "product_name": product_name,
                "quantity_sold": quantity_sold,
                "revenue": revenue,
            }
            for (
                product_id,
                product_name,
                quantity_sold,
                revenue,
            ) in rows
        ],
    }


# --------------------------------------------------
# Daily Sales
# --------------------------------------------------

@router.get("/sales/daily")
async def daily_sales(
    limit: int = Query(
        default=30,
        ge=1,
        le=365,
    ),
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(db)

    rows = await repo.daily_sales(
        limit=limit
    )

    return {
        "success": True,
        "message": "Daily sales fetched successfully",
        "data": [
            {
                "date": sale_date,
                "orders": orders,
                "revenue": revenue,
            }
            for (
                sale_date,
                orders,
                revenue,
            ) in rows
        ],
    }