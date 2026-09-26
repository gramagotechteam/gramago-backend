# from fastapi import APIRouter
# from fastapi.responses import (
#     RedirectResponse,
# )

# # from app.web.routes import (
# #     auth,
# #     dashboard,
# # )


# from app.web.routes import (
#     auth,
#     categories,
#     dashboard,
#     products,
#     inventory,
#     orders,
#     customers,
#     reports,
#     audit_logs
    
    
    
# )



# admin_web_router = APIRouter(
#     prefix="/admin"
# )


# @admin_web_router.get("")
# async def admin_home():

#     return RedirectResponse(
#         url="/admin/dashboard",
#         status_code=303,
#     )


# admin_web_router.include_router(
#     auth.router
# )

# admin_web_router.include_router(
#     dashboard.router
# )

# admin_web_router.include_router(
#     categories.router
# )

# admin_web_router.include_router(
#     products.router
# )

# admin_web_router.include_router(
#     inventory.router
# )


# admin_web_router.include_router(
#     orders.router
# )



# admin_web_router.include_router(
#     customers.router
# )
# admin_web_router.include_router(
#     reports.router
# )


# admin_web_router.include_router(
#     audit_logs.router
# )


from fastapi import APIRouter

# from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.web.routes import (
    admin_users,
    audit_logs,
    auth,
    categories,
    customers,
    dashboard,
    inventory,
    orders,
    products,
    profile,
    reports,
    commerce_settings,
)


admin_web_router = APIRouter(
    prefix="/admin"
)




# ==========================================
# Admin root
# ==========================================

@admin_web_router.get("")
async def admin_root():

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=303,
    )


admin_web_router.include_router(
    auth.router
)

admin_web_router.include_router(
    dashboard.router
)

admin_web_router.include_router(
    categories.router
)

admin_web_router.include_router(
    products.router
)

admin_web_router.include_router(
    inventory.router
)

admin_web_router.include_router(
    orders.router
)

admin_web_router.include_router(
    customers.router
)

admin_web_router.include_router(
    reports.router
)

admin_web_router.include_router(
    audit_logs.router
)

admin_web_router.include_router(
    admin_users.router
)

admin_web_router.include_router(
    profile.router
)

admin_web_router.include_router(
    commerce_settings.router
)