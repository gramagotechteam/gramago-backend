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
# from app.repositories.dashboard_repository import (
#     DashboardRepository,
# )
# from app.schemas.order import (
#     AdminOrderListResponse,
# )
# from app.services.dashboard_service import (
#     DashboardService,
# )


# router = APIRouter()


# @router.get("/summary")
# async def dashboard_summary(
#     current_user: User = Depends(
#         require_admin
#     ),

#     db: AsyncSession = Depends(get_db),
# ):

#     service = DashboardService(db)

#     summary = await service.get_summary()

#     return {
#         "success": True,
#         "message": (
#             "Dashboard summary fetched"
#         ),
#         "data": summary,
#     }
    
    

# @router.get("/recent-orders")
# async def recent_orders(
#     current_user: User = Depends(
#         require_admin
#     ),

#     db: AsyncSession = Depends(get_db),
# ):

#     repository = DashboardRepository(
#         db
#     )

#     orders = await repository.recent_orders(
#         10
#     )

#     return {
#         "success": True,
#         "message": (
#             "Recent orders fetched"
#         ),
#         "data": [
#             AdminOrderListResponse
#             .model_validate(order)

#             for order in orders
#         ],
#     }
    


from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.repositories.dashboard_repository import (
    DashboardRepository,
)
from app.schemas.order import (
    AdminOrderListResponse,
)
from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter()


@router.get("/summary")
async def dashboard_summary(
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)

    summary = await service.get_summary()

    return {
        "success": True,
        "message": "Dashboard summary fetched successfully",
        "data": summary,
    }


@router.get("/recent-orders")
async def recent_orders(
    current_user: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    repository = DashboardRepository(
        db
    )

    orders = await repository.recent_orders(
        limit=10
    )

    return {
        "success": True,
        "message": "Recent orders fetched successfully",
        "data": [
            AdminOrderListResponse.model_validate(
                order
            )
            for order in orders
        ],
    }