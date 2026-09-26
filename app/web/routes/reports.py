from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.report_repository import (
    ReportRepository,
)
from app.web.dependencies import (
    get_admin_web_user,
)
from app.web.templates import templates


# from fastapi.templating import (
#     Jinja2Templates,
# )


# templates = Jinja2Templates(
#     directory="app/templates"
# )


router = APIRouter()


@router.get("/reports")
async def reports_page(
    request: Request,

    days: int = Query(
        default=30,
        ge=7,
        le=365,
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = ReportRepository(
        db
    )


    # ------------------------------------------
    # KPI
    # ------------------------------------------

    summary = (
        await repository.report_summary()
    )

    today_revenue = (
        await repository.today_revenue()
    )

    today_orders = (
        await repository.today_orders()
    )

    average_order_value = (
    await repository
    .average_order_value()
)
    
    
    completed_total = (
    summary["delivered_orders"]
    + summary["cancelled_orders"]
    + summary["failed_orders"]
)

    delivery_success_rate = (
        (
            summary["delivered_orders"]
            / completed_total
        )
        * 100
        if completed_total > 0
        else 0
    )
    # ------------------------------------------
    # Order Status
    # ------------------------------------------

    order_status_rows = (
        await repository
        .order_status_summary()
    )

    order_status_data = [
        {
            "status": status,
            "count": count,
        }
        for status, count
        in order_status_rows
    ]


    # ------------------------------------------
    # Payment Status
    # ------------------------------------------

    payment_status_rows = (
        await repository
        .payment_status_summary()
    )

    payment_status_data = [
        {
            "status": status,
            "count": count,
        }
        for status, count
        in payment_status_rows
    ]


    # ------------------------------------------
    # Top Products
    # ------------------------------------------

    top_product_rows = (
        await repository.top_products(
            limit=10
        )
    )

    top_products = [
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
        )
        in top_product_rows
    ]


    # ------------------------------------------
    # Daily Sales
    # ------------------------------------------

    daily_rows = (
        await repository.daily_sales(
            days=days
        )
    )

    daily_sales = [
        {
            "date": str(sale_date),
            "orders": orders,
            "revenue": float(
                revenue or 0
            ),
        }
        for (
            sale_date,
            orders,
            revenue,
        )
        in daily_rows
    ]


    return templates.TemplateResponse(
        request=request,
        name="admin/reports/index.html",
        context={
            "admin": current_admin,

            "summary": summary,

            "today_revenue": (
                today_revenue
            ),
            
            "delivery_success_rate":
    round(
        delivery_success_rate,
        2
    ),
            
            "average_order_value": round(
    average_order_value,2),

            "today_orders": (
                today_orders
            ),

            "order_status_data": (
                order_status_data
            ),

            "payment_status_data": (
                payment_status_data
            ),

            "top_products": (
                top_products
            ),

            "daily_sales": (
                daily_sales
            ),

            "days": days,

            "active_page": (
                "reports"
            ),
        },
    )