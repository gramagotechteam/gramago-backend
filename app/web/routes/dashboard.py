from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.dashboard_repository import (
    DashboardRepository,
)
from app.services.dashboard_service import (
    DashboardService,
)
from app.web.dependencies import (
    get_admin_web_user,
)


from sqlalchemy import (
    func,
    select,
)

from app.models.delivery_assignment import (
    DeliveryAssignment,
)

from app.models.delivery_partner import (
    DeliveryPartnerProfile,
)

from app.models.order import Order

from app.models.user import User

ACTIVE_DELIVERY_STATUSES = {
    "ASSIGNED",
    "ACCEPTED",
    "PICKED_UP",
    "OUT_FOR_DELIVERY",
}

# from app.web.templates import templates


router = APIRouter()


# from app.web.router import templates


from app.web.templates import templates

# from fastapi.templating import (
#     Jinja2Templates,
# )


# templates = Jinja2Templates(
#     directory="app/templates"
# )


@router.get("/dashboard")
async def dashboard(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = DashboardService(db)

    repository = DashboardRepository(
        db
    )

    summary = await service.get_summary()

    recent_orders = (
        await repository.recent_orders(
            limit=10
        )
    )
    



    # ============================================================
    # DELIVERY DASHBOARD
    # ============================================================

    ready_delivery_result = await db.execute(
        select(
            func.count(
                Order.id
            )
        )
        .where(
            Order.order_status.in_(
                [
                    "PACKED",
                    "READY_FOR_PICKUP",
                ]
            )
        )
    )

    ready_delivery_count = int(
        ready_delivery_result.scalar()
        or 0
    )



    active_delivery_result = await db.execute(
        select(
            func.count(
                DeliveryAssignment.id
            )
        )
        .where(
            DeliveryAssignment.status.in_(
                ACTIVE_DELIVERY_STATUSES
            )
        )
    )

    active_delivery_count = int(
        active_delivery_result.scalar()
        or 0
    )



    active_delivery_partner_result = await db.execute(
        select(
            func.count(
                func.distinct(
                    DeliveryAssignment.delivery_partner_id
                )
            )
        )
        .where(
            DeliveryAssignment.status.in_(
                ACTIVE_DELIVERY_STATUSES
            )
        )
    )

    active_delivery_partner_count = int(
        active_delivery_partner_result.scalar()
        or 0
    )




    online_partner_result = await db.execute(
        select(
            func.count(
                DeliveryPartnerProfile.id
            )
        )
        .join(
            User,
            User.id
            == DeliveryPartnerProfile.user_id,
        )
        .where(
            User.is_active.is_(True),
            DeliveryPartnerProfile.is_approved.is_(True),
            DeliveryPartnerProfile.is_online.is_(True),
        )
    )

    online_partner_count = int(
        online_partner_result.scalar()
        or 0
    )




    total_partner_result = await db.execute(
        select(
            func.count(
                DeliveryPartnerProfile.id
            )
        )
    )

    total_delivery_partner_count = int(
        total_partner_result.scalar()
        or 0
    )


    pending_partner_result = await db.execute(
        select(
            func.count(
                DeliveryPartnerProfile.id
            )
        )
        .where(
            DeliveryPartnerProfile.is_approved.is_(
                False
            )
        )
    )

    pending_partner_count = int(
        pending_partner_result.scalar()
        or 0
    )



    delivery_status_result = await db.execute(
        select(
            DeliveryAssignment.status,
            func.count(
                DeliveryAssignment.id
            ),
        )
        .group_by(
            DeliveryAssignment.status
        )
    )

    delivery_status_counts = {
        status: count
        for status, count
        in delivery_status_result.all()
    }



    assigned_delivery_count = (
        delivery_status_counts.get(
            "ASSIGNED",
            0,
        )
    )

    accepted_delivery_count = (
        delivery_status_counts.get(
            "ACCEPTED",
            0,
        )
    )

    picked_up_delivery_count = (
        delivery_status_counts.get(
            "PICKED_UP",
            0,
        )
    )

    out_for_delivery_count = (
        delivery_status_counts.get(
            "OUT_FOR_DELIVERY",
            0,
        )
    )

    delivered_delivery_count = (
        delivery_status_counts.get(
            "DELIVERED",
            0,
        )
    )

    rejected_delivery_count = (
        delivery_status_counts.get(
            "REJECTED",
            0,
        )
    )

    failed_delivery_count = (
        delivery_status_counts.get(
            "FAILED",
            0,
        )
    )



    recent_delivery_result = await db.execute(
        select(
            DeliveryAssignment,
            Order,
            User,
        )
        .join(
            Order,
            Order.id
            == DeliveryAssignment.order_id,
        )
        .join(
            User,
            User.id
            == DeliveryAssignment.delivery_partner_id,
        )
        .where(
            DeliveryAssignment.status.in_(
                ACTIVE_DELIVERY_STATUSES
            )
        )
        .order_by(
            DeliveryAssignment.assigned_at.desc()
        )
        .limit(
            5
        )
    )

    recent_active_deliveries = []

    for (
        assignment,
        order,
        partner,
    ) in recent_delivery_result.all():

        recent_active_deliveries.append(
            {
                "assignment":
                    assignment,

                "order":
                    order,

                "partner":
                    partner,
            }
        )
        
    
    
    
    
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "admin": current_admin,
            "summary": summary,
            "recent_orders": (
                recent_orders
            ),
            "active_page": (
                "dashboard"
            ),
            
            
            "ready_delivery_count":
    ready_delivery_count,

"active_delivery_count":
    active_delivery_count,

"active_delivery_partner_count":
    active_delivery_partner_count,

"online_partner_count":
    online_partner_count,

"total_delivery_partner_count":
    total_delivery_partner_count,

"pending_partner_count":
    pending_partner_count,

"assigned_delivery_count":
    assigned_delivery_count,

"accepted_delivery_count":
    accepted_delivery_count,

"picked_up_delivery_count":
    picked_up_delivery_count,

"out_for_delivery_count":
    out_for_delivery_count,

"delivered_delivery_count":
    delivered_delivery_count,

"rejected_delivery_count":
    rejected_delivery_count,

"failed_delivery_count":
    failed_delivery_count,

"recent_active_deliveries":
    recent_active_deliveries,
    
        },
    )
    




