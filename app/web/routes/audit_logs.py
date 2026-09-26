from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.admin_audit_repository import (
    AdminAuditRepository,
)
from app.web.dependencies import (
    get_super_admin_web_user,
)
# from app.web.templates import templates


from app.web.templates import templates
# from fastapi.templating import (
#     Jinja2Templates,
# )


# templates = Jinja2Templates(
#     directory="app/templates"
# )


router = APIRouter()


# ==========================================
# Audit Log List
# ==========================================

@router.get("/audit-logs")
async def audit_log_list(
    request: Request,

    search: str | None = Query(
        default=None
    ),

    action: str | None = Query(
        default=None
    ),

    entity_type: str | None = Query(
        default=None
    ),

    admin_user_id: int | None = Query(
        default=None
    ),

    page: int = Query(
        default=1,
        ge=1,
    ),

    limit: int = Query(
        default=25,
        ge=1,
        le=100,
    ),

    current_admin: User = Depends(
        get_super_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = (
        AdminAuditRepository(db)
    )


    rows, total = (
        await repository.list_logs(

            search=search,

            action=action,

            entity_type=entity_type,

            admin_user_id=(
                admin_user_id
            ),

            page=page,

            limit=limit,
        )
    )


    actions = (
        await repository.get_actions()
    )

    entity_types = (
        await repository
        .get_entity_types()
    )

    admin_users = (
        await repository
        .get_admin_users()
    )


    total_pages = (
        ceil(total / limit)
        if total > 0
        else 0
    )


    logs = []

    for log, admin_user in rows:

        logs.append(
            {
                "log": log,
                "admin_user": (
                    admin_user
                ),
            }
        )


    return templates.TemplateResponse(
        request=request,
        name=(
            "admin/audit_logs/list.html"
        ),
        context={
            "admin": current_admin,

            "logs": logs,

            "actions": actions,

            "entity_types": (
                entity_types
            ),

            "admin_users": (
                admin_users
            ),

            "search": (
                search or ""
            ),

            "selected_action": (
                action or ""
            ),

            "selected_entity_type": (
                entity_type or ""
            ),

            "selected_admin_user_id": (
                admin_user_id
            ),

            "page": page,

            "limit": limit,

            "total": total,

            "total_pages": (
                total_pages
            ),

            "active_page": (
                "audit"
            ),
        },
    )


# ==========================================
# Audit Log Detail
# ==========================================

@router.get(
    "/audit-logs/{log_id}"
)
async def audit_log_detail(
    log_id: int,

    request: Request,

    current_admin: User = Depends(
        get_super_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = (
        AdminAuditRepository(db)
    )


    row = await repository.get_by_id(
        log_id
    )


    if not row:

        raise HTTPException(
            status_code=404,
            detail=(
                "Audit log not found"
            ),
        )


    log, admin_user = row


    return templates.TemplateResponse(
        request=request,
        name=(
            "admin/audit_logs/detail.html"
        ),
        context={
            "admin": current_admin,

            "log": log,

            "admin_user": (
                admin_user
            ),

            "active_page": (
                "audit"
            ),
        },
    )