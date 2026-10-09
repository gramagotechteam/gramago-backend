

from app.api.v1.endpoints import (
    admin,
    auth,
    users,
)

from fastapi import APIRouter

# from app.api.v1.endpoints import auth, users
from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    admin_categories,
    admin_dashboard,
    admin_inventory,
    admin_orders,
    admin_products,
    admin_reports,
    addresses,
    auth,
    cart,
    categories,
    checkout,
    notifications,
    orders,
    products,
    users,
    device_tokens,
    admin_notifications,
    admin_commerce_settings,
    commerce,
    admin_delivery_partners,
    delivery_auth,
    delivery_status,
    admin_delivery_assignments,
    delivery_orders,
)

from app.api.v1.endpoints import (
    delivery_notifications,
)



api_router = APIRouter()


api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)


api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)


api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"],
)


api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"],
)


api_router.include_router(
    admin_categories.router,
    prefix="/admin/categories",
    tags=["Admin Categories"],
)

api_router.include_router(
    products.router,
    prefix="/products",
    tags=["Products"],
)


api_router.include_router(
    admin_products.router,
    prefix="/admin/products",
    tags=["Admin Products"],
)


api_router.include_router(
    admin_inventory.router,
    prefix="/admin/inventory",
    tags=["Admin Inventory"],
)

api_router.include_router(
    addresses.router,
    prefix="/addresses",
    tags=["Addresses"],
)

api_router.include_router(
    cart.router,
    prefix="/cart",
    tags=["Cart"],
)

api_router.include_router(
    checkout.router,
    prefix="/checkout",
    tags=["Checkout"],
)

api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["Orders"],
)

api_router.include_router(

    admin_orders.router,

    prefix="/admin/orders",

    tags=["Admin Orders"],
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)

api_router.include_router(
    admin_dashboard.router,
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"],
)


api_router.include_router(
    admin_reports.router,
    prefix="/admin/reports",
    tags=["Admin Reports"],
)

api_router.include_router(
    device_tokens.router,
    prefix="/device-tokens",
    tags=["Device Tokens"],
)


api_router.include_router(
    admin_notifications.router,
    prefix="/admin/notifications",
    tags=["Admin Notifications"],
)


api_router.include_router(
    admin_commerce_settings.router,
    prefix="/admin/commerce-settings",
    tags=["Admin Commerce Settings"],
)


api_router.include_router(
    commerce.router,
    prefix="/commerce",
    tags=["Commerce"],
)



api_router.include_router(
    admin_delivery_partners.router,
    prefix="/admin/delivery-partners",
    tags=["Admin Delivery Partners"],
)



api_router.include_router(
    delivery_auth.router,
    prefix="/delivery/auth",
    tags=["Delivery Authentication"],
)




api_router.include_router(
    delivery_status.router,
    prefix="/delivery/status",
    tags=["Delivery Status"],
)



api_router.include_router(
    admin_delivery_assignments.router,
    prefix="/admin/delivery-assignments",
    tags=["Admin Delivery Assignments"],
)




api_router.include_router(
    delivery_orders.router,
    prefix="/delivery/orders",
    tags=["Delivery Orders"],
)


api_router.include_router(
    delivery_notifications.router,

    prefix=(
        "/delivery/notifications"
    ),

    tags=[
        "Delivery Notifications"
    ],
)
