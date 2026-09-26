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
        },
    )