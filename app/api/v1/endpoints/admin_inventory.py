from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.inventory import (
    StockAddRequest,
)
from app.services.inventory_service import (
    InventoryService,
)


router = APIRouter()


@router.post("/{product_id}/stock")
async def add_stock(
    product_id: int,
    data: StockAddRequest,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    service = InventoryService(db)

    inventory = await service.add_stock(
        product_id=product_id,
        quantity=data.quantity,
        user_id=current_user.id,
        note=data.note,
    )

    return {
        "success": True,
        "message": "Stock added successfully",
        "data": {
            "product_id": product_id,
            "available_quantity": (
                inventory.available_quantity
            ),
            "reserved_quantity": (
                inventory.reserved_quantity
            ),
        },
    }
    


from app.schemas.inventory import (
    DamagedStockRequest,
    InventoryAdjustmentRequest,
    ReorderLevelRequest,
    StockAddRequest,
)



@router.post("/{product_id}/adjust")
async def adjust_inventory(
    product_id: int,
    data: InventoryAdjustmentRequest,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    service = InventoryService(db)

    inventory = (
        await service.manual_adjustment(
            product_id=product_id,
            direction=data.direction,
            quantity=data.quantity,
            user_id=current_user.id,
            note=data.note,
        )
    )

    return {
        "success": True,
        "message": "Inventory adjusted successfully",
        "data": {
            "available_quantity": (
                inventory.available_quantity
            ),
            "reserved_quantity": (
                inventory.reserved_quantity
            ),
        },
    }
    




@router.post("/{product_id}/damaged")
async def damaged_stock(
    product_id: int,
    data: DamagedStockRequest,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    service = InventoryService(db)

    inventory = await service.mark_damaged(
        product_id=product_id,
        quantity=data.quantity,
        user_id=current_user.id,
        note=data.note,
    )

    return {
        "success": True,
        "message": "Damaged stock recorded successfully",
        "data": {
            "available_quantity": (
                inventory.available_quantity
            ),
        },
    }
    



@router.patch("/{product_id}/reorder-level")
async def update_reorder_level(
    product_id: int,
    data: ReorderLevelRequest,

    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    service = InventoryService(db)

    inventory = (
        await service.set_reorder_level(
            product_id,
            data.reorder_level,
        )
    )

    return {
        "success": True,
        "message": "Reorder level updated",
        "data": {
            "product_id": product_id,
            "reorder_level": (
                inventory.reorder_level
            ),
        },
    }
    




@router.get("/low-stock")
async def low_stock(
    current_user: User = Depends(
        require_admin
    ),

    db: AsyncSession = Depends(get_db),
):

    service = InventoryService(db)

    rows = await service.get_low_stock()

    data = []

    for inventory, product in rows:

        sellable = (
            inventory.available_quantity
            - inventory.reserved_quantity
        )

        data.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "available_quantity": (
                    inventory.available_quantity
                ),
                "reserved_quantity": (
                    inventory.reserved_quantity
                ),
                "sellable_quantity": sellable,
                "reorder_level": (
                    inventory.reorder_level
                ),
            }
        )

    return {
        "success": True,
        "message": "Low stock products fetched",
        "data": data,
    }
    
    
