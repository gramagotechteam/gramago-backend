# from fastapi import (
#     APIRouter,
#     Depends,
#     Form,
#     Request,
# )
# from fastapi.responses import (
#     RedirectResponse,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.security import (
#     verify_password,
# )
# from app.db.session import get_db
# from app.repositories.user_repository import (
#     UserRepository,
# )
# # from app.web.router import templates
# from app.web.templates import templates

# router = APIRouter()



# from app.web.csrf import validate_csrf

# # ---------------------------------------
# # Login Page
# # ---------------------------------------

# @router.get("/login",
#              dependencies=[
#         Depends(validate_csrf)
#     ],)
# async def admin_login_page(
#     request: Request,
# ):

#     if request.session.get(
#         "admin_user_id"
#     ):

#         return RedirectResponse(
#             url="/admin/dashboard",
#             status_code=303,
#         )

#     return templates.TemplateResponse(
#         request=request,
#         name="admin/login.html",
#         context={
#             "error": None,
#         },
#     )


# # ---------------------------------------
# # Login Submit
# # ---------------------------------------
# from app.web.csrf import validate_csrf


# @router.post("/login",dependencies=[
#         Depends(validate_csrf)
#     ],)
# async def admin_login(
#     request: Request,

#     identifier: str = Form(...),

#     password: str = Form(...),

#     db: AsyncSession = Depends(get_db),
# ):

#     repository = UserRepository(db)

#     identifier = identifier.strip()

#     if "@" in identifier:
#         identifier = identifier.lower()

#     user = await repository.get_by_identifier(
#         identifier
#     )

#     if (
#         not user
#         or not verify_password(
#             password,
#             user.password_hash,
#         )
#     ):

#         return templates.TemplateResponse(
#             request=request,
#             name="admin/login.html",
#             context={
#                 "error": (
#                     "Invalid email/phone or password"
#                 ),
#             },
#             status_code=401,
#         )

#     if not user.is_active:

#         return templates.TemplateResponse(
#             request=request,
#             name="admin/login.html",
#             context={
#                 "error": (
#                     "Your account is disabled"
#                 ),
#             },
#             status_code=403,
#         )

#     if user.role not in {
#         "ADMIN",
#         "SUPER_ADMIN",
#     }:

#         return templates.TemplateResponse(
#             request=request,
#             name="admin/login.html",
#             context={
#                 "error": (
#                     "You do not have "
#                     "admin access"
#                 ),
#             },
#             status_code=403,
#         )

#     request.session.clear()

#     request.session[
#         "admin_user_id"
#     ] = user.id

#     return RedirectResponse(
#         url="/admin/dashboard",
#         status_code=303,
#     )


# # ---------------------------------------
# # Logout
# # ---------------------------------------

# @router.post("/logout",
#               dependencies=[
#         Depends(validate_csrf)
#     ],)
# async def admin_logout(
#     request: Request,
# ):

#     request.session.clear()

#     return RedirectResponse(
#         url="/admin/login",
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

from app.core.security import verify_password
from app.db.session import get_db
from app.repositories.user_repository import (
    UserRepository,
)
from app.web.csrf import validate_csrf
from app.web.templates import templates


router = APIRouter()


# ---------------------------------------
# Login Page
# ---------------------------------------

# @router.get("/login")
# async def admin_login_page(
#     request: Request,
# ):

#     if request.session.get(
#         "admin_user_id"
#     ):

#         return RedirectResponse(
#             url="/admin/dashboard",
#             status_code=303,
#         )

#     return templates.TemplateResponse(
#         request=request,
#         name="admin/login.html",
#         context={
#             "error": None,
#         },
#     )


@router.get("/login")
async def admin_login_page(
    request: Request,

    password_changed: int | None = None,
):

    if request.session.get(
        "admin_user_id"
    ):

        return RedirectResponse(
            url="/admin/dashboard",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "error": None,

            "success": (
                "Password changed successfully. "
                "Please login again."
                if password_changed == 1
                else None
            ),
        },
    )


# ---------------------------------------
# Login Submit
# ---------------------------------------

@router.post(
    "/login",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def admin_login(
    request: Request,

    identifier: str = Form(...),

    password: str = Form(...),

    db: AsyncSession = Depends(get_db),
):

    repository = UserRepository(db)

    identifier = identifier.strip()

    if "@" in identifier:
        identifier = identifier.lower()

    user = await repository.get_by_identifier(
        identifier
    )

    if (
        not user
        or not verify_password(
            password,
            user.password_hash,
        )
    ):

        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={
                "error": (
                    "Invalid email/phone or password"
                ),
            },
            status_code=401,
        )

    if not user.is_active:

        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={
                "error": (
                    "Your account is disabled"
                ),
            },
            status_code=403,
        )

    # if user.role not in {
    #     "ADMIN",
    #     "SUPER_ADMIN",
    # }:
    role = (
    user.role.strip().upper()
    if user.role
    else ""
)

    if role not in {
        "ADMIN",
        "SUPER_ADMIN",
    }:

        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={
                "error": (
                    "You do not have admin access"
                ),
            },
            status_code=403,
        )

    # Clear old session data
    request.session.clear()

    # Store logged-in admin
    request.session[
        "admin_user_id"
    ] = user.id

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=303,
    )


# ---------------------------------------
# Logout
# ---------------------------------------

@router.post(
    "/logout",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def admin_logout(
    request: Request,
):

    request.session.clear()

    return RedirectResponse(
        url="/admin/login",
        status_code=303,
    )