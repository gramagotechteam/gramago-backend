# from fastapi import (
#     APIRouter,
#     Depends,
#     Form,
#     HTTPException,
#     Request,
# )
# from fastapi.responses import RedirectResponse
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.security import (
#     hash_password,
#     verify_password,
# )
# from app.db.session import get_db
# from app.models.user import User
# from app.services.audit_service import (
#     AuditService,
# )
# from app.web.csrf import validate_csrf
# from app.web.dependencies import (
#     get_admin_web_user,
# )
# from app.web.flash import flash
# from app.web.templates import templates


# router = APIRouter()


# @router.get("/profile")
# async def profile_page(
#     request: Request,

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),
# ):

#     return templates.TemplateResponse(
#         request=request,
#         name="admin/profile/index.html",
#         context={
#             "admin": current_admin,
#             "active_page": "profile",
#         },
#     )


# @router.post(
#     "/profile/change-password",
#     dependencies=[
#         Depends(validate_csrf)
#     ],
# )
# async def change_password(
#     request: Request,

#     current_password: str = Form(...),
#     new_password: str = Form(...),
#     confirm_password: str = Form(...),

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(get_db),
# ):

#     if not verify_password(
#         current_password,
#         current_admin.password_hash,
#     ):

#         flash(
#             request,
#             "Current password is incorrect.",
#             "danger",
#         )

#         return RedirectResponse(
#             "/admin/profile",
#             status_code=303,
#         )


#     if new_password != confirm_password:

#         flash(
#             request,
#             "New passwords do not match.",
#             "danger",
#         )

#         return RedirectResponse(
#             "/admin/profile",
#             status_code=303,
#         )


#     if len(new_password) < 8:

#         flash(
#             request,
#             "Password must be at least 8 characters.",
#             "danger",
#         )

#         return RedirectResponse(
#             "/admin/profile",
#             status_code=303,
#         )


#     current_admin.password_hash = (
#         hash_password(new_password)
#     )


#     await AuditService(db).log(
#         admin_user_id=current_admin.id,
#         action="ADMIN_PASSWORD_CHANGED",
#         entity_type="USER",
#         entity_id=current_admin.id,
#         description=(
#             "Admin changed their password"
#         ),
#     )


#     await db.commit()


#     # Force fresh login after password change
#     request.session.clear()


#     return RedirectResponse(
#         "/admin/login",
#         status_code=303,
#     )



from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.services.audit_service import (
    AuditService,
)
from app.web.csrf import validate_csrf
from app.web.dependencies import (
    get_admin_web_user,
)
from app.web.flash import flash
from app.web.templates import templates


router = APIRouter()


# ==========================================
# Profile Page
# ==========================================

@router.get("/profile")
async def admin_profile(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),
):

    return templates.TemplateResponse(
        request=request,
        name="admin/profile/index.html",
        context={
            "admin": current_admin,
            "active_page": "profile",
        },
    )


# ==========================================
# Change Password
# ==========================================

@router.post(
    "/profile/change-password",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def change_password(
    request: Request,

    current_password: str = Form(...),

    new_password: str = Form(...),

    confirm_password: str = Form(...),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    # --------------------------------------
    # Verify current password
    # --------------------------------------

    if not verify_password(
        current_password,
        current_admin.password_hash,
    ):

        flash(
            request,
            "Current password is incorrect.",
            "danger",
        )

        return RedirectResponse(
            url="/admin/profile",
            status_code=303,
        )


    # --------------------------------------
    # Match new passwords
    # --------------------------------------

    if new_password != confirm_password:

        flash(
            request,
            "New password and confirmation do not match.",
            "danger",
        )

        return RedirectResponse(
            url="/admin/profile",
            status_code=303,
        )


    # --------------------------------------
    # Minimum password rule
    # --------------------------------------

    if len(new_password) < 8:

        flash(
            request,
            "New password must be at least 8 characters.",
            "danger",
        )

        return RedirectResponse(
            url="/admin/profile",
            status_code=303,
        )


    # --------------------------------------
    # Prevent reusing current password
    # --------------------------------------

    if verify_password(
        new_password,
        current_admin.password_hash,
    ):

        flash(
            request,
            "New password must be different from your current password.",
            "danger",
        )

        return RedirectResponse(
            url="/admin/profile",
            status_code=303,
        )


    # --------------------------------------
    # Update password
    # --------------------------------------

    current_admin.password_hash = (
        hash_password(
            new_password
        )
    )


    # --------------------------------------
    # Audit
    # --------------------------------------

    audit_service = AuditService(db)

    await audit_service.log(
        admin_user_id=current_admin.id,

        action="ADMIN_PASSWORD_CHANGED",

        entity_type="USER",

        entity_id=current_admin.id,

        description=(
            "Admin changed their password"
        ),
    )


    await db.commit()


    # --------------------------------------
    # Force login again
    # --------------------------------------

    request.session.clear()


    return RedirectResponse(
        url="/admin/login?password_changed=1",
        status_code=303,
    )