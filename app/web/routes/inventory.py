from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    Request,
)
from fastapi.responses import (
    RedirectResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.inventory_repository import (
    InventoryRepository,
)
from app.services.audit_service import (
    AuditService,
)
from app.services.inventory_service import (
    InventoryService,
)
from app.web.dependencies import (
    get_admin_web_user,
)
from app.web.templates import templates

from app.web.csrf import validate_csrf

# from fastapi.templating import (
#     Jinja2Templates,
# )


# templates = Jinja2Templates(
#     directory="app/templates"
# )


router = APIRouter()


# ==================================================
# Inventory List
# ==================================================

@router.get("/inventory")
async def inventory_list(
    request: Request,

    search: str | None = Query(
        default=None
    ),

    low_stock: bool = Query(
        default=False
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = InventoryRepository(
        db
    )

    rows = await repository.list_inventory(
        search=search,
        low_stock_only=low_stock,
    )

    inventory_items = []

    for inventory, product in rows:

        sellable_quantity = (
            inventory.available_quantity
            - inventory.reserved_quantity
        )

        inventory_items.append(
            {
                "inventory": inventory,
                "product": product,
                "sellable_quantity": (
                    sellable_quantity
                ),
                "is_low_stock": (
                    sellable_quantity
                    <= inventory.reorder_level
                ),
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/inventory/list.html",
        context={
            "admin": current_admin,

            "items": inventory_items,

            "search": (
                search or ""
            ),

            "low_stock": (
                low_stock
            ),

            "active_page": (
                "inventory"
            ),
        },
    )


# ==================================================
# Inventory Detail
# ==================================================

@router.get(
    "/inventory/{product_id}"
)
async def inventory_detail(
    product_id: int,
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    repository = InventoryRepository(
        db
    )

    product = await repository.get_product(
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    inventory = (
        await repository.get_by_product_id(
            product_id
        )
    )

    if not inventory:

        raise HTTPException(
            status_code=404,
            detail="Inventory not found",
        )

    transactions = (
        await repository.get_transactions(
            product_id,
            limit=100,
        )
    )

    sellable_quantity = (
        inventory.available_quantity
        - inventory.reserved_quantity
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/inventory/detail.html",
        context={
            "admin": current_admin,

            "product": product,

            "inventory": inventory,

            "transactions": (
                transactions
            ),

            "sellable_quantity": (
                sellable_quantity
            ),

            "is_low_stock": (
                sellable_quantity
                <= inventory.reorder_level
            ),

            "active_page": (
                "inventory"
            ),

            "error": None,
        },
    )


# ==================================================
# Add Stock
# ==================================================

@router.post(
    "/inventory/{product_id}/stock",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def add_stock(
    product_id: int,

    quantity: Decimal = Form(...),

    note: str | None = Form(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = InventoryService(
        db
    )

    inventory = await service.add_stock(
        product_id=product_id,
        quantity=quantity,
        user_id=current_admin.id,
        note=note,
    )

    # InventoryService already committed,
    # so audit requires another commit.

    audit = AuditService(db)

    await audit.log(
        admin_user_id=current_admin.id,

        action="INVENTORY_STOCK_IN",

        entity_type="PRODUCT",

        entity_id=product_id,

        description=(
            f"Added {quantity} stock"
        ),

        new_data={
            "quantity_added": str(
                quantity
            ),

            "available_quantity": str(
                inventory.available_quantity
            ),
        },
    )

    await db.commit()

    return RedirectResponse(
        url=(
            f"/admin/inventory/"
            f"{product_id}"
        ),
        status_code=303,
    )


# ==================================================
# Manual Adjustment
# ==================================================

@router.post(
    "/inventory/{product_id}/adjust",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def adjust_stock(
    product_id: int,

    direction: str = Form(...),

    quantity: Decimal = Form(...),

    note: str = Form(...),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    if direction not in {
        "ADD",
        "REMOVE",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Adjustment direction "
                "must be ADD or REMOVE"
            ),
        )

    service = InventoryService(
        db
    )

    inventory = (
        await service.manual_adjustment(
            product_id=product_id,
            direction=direction,
            quantity=quantity,
            user_id=current_admin.id,
            note=note,
        )
    )

    audit = AuditService(db)

    await audit.log(
        admin_user_id=current_admin.id,

        action=(
            "INVENTORY_ADJUSTMENT"
        ),

        entity_type="PRODUCT",

        entity_id=product_id,

        description=(
            f"Manual inventory "
            f"{direction}: {quantity}"
        ),

        new_data={
            "direction": direction,
            "quantity": str(quantity),
            "available_quantity": str(
                inventory.available_quantity
            ),
        },
    )

    await db.commit()

    return RedirectResponse(
        url=(
            f"/admin/inventory/"
            f"{product_id}"
        ),
        status_code=303,
    )


# ==================================================
# Damaged Stock
# ==================================================

@router.post(
    "/inventory/{product_id}/damaged",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def damaged_stock(
    product_id: int,

    quantity: Decimal = Form(...),

    note: str | None = Form(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = InventoryService(
        db
    )

    inventory = (
        await service.mark_damaged(
            product_id=product_id,
            quantity=quantity,
            user_id=current_admin.id,
            note=note,
        )
    )

    audit = AuditService(db)

    await audit.log(
        admin_user_id=current_admin.id,

        action="INVENTORY_DAMAGED",

        entity_type="PRODUCT",

        entity_id=product_id,

        description=(
            f"Marked {quantity} stock "
            f"as damaged"
        ),

        new_data={
            "damaged_quantity": str(
                quantity
            ),

            "available_quantity": str(
                inventory.available_quantity
            ),
        },
    )

    await db.commit()

    return RedirectResponse(
        url=(
            f"/admin/inventory/"
            f"{product_id}"
        ),
        status_code=303,
    )


# ==================================================
# Reorder Level
# ==================================================

@router.post(
    "/inventory/{product_id}/reorder-level",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def reorder_level(
    product_id: int,

    reorder_level: Decimal = Form(...),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(get_db),
):

    service = InventoryService(
        db
    )

    inventory = (
        await service.set_reorder_level(
            product_id=product_id,
            reorder_level=reorder_level,
        )
    )

    audit = AuditService(db)

    await audit.log(
        admin_user_id=current_admin.id,

        action=(
            "INVENTORY_REORDER_LEVEL"
        ),

        entity_type="PRODUCT",

        entity_id=product_id,

        description=(
            "Inventory reorder level updated"
        ),

        new_data={
            "reorder_level": str(
                inventory.reorder_level
            ),
        },
    )

    await db.commit()

    return RedirectResponse(
        url=(
            f"/admin/inventory/"
            f"{product_id}"
        ),
        status_code=303,
    )