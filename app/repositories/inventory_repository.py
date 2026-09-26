from sqlalchemy import (
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory import Inventory
from app.models.inventory_transaction import (
    InventoryTransaction,
)
from app.models.product import Product


class InventoryRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # -----------------------------------------
    # Admin inventory list
    # -----------------------------------------

    async def list_inventory(
        self,
        *,
        search: str | None = None,
        low_stock_only: bool = False,
    ):

        stmt = (
            select(
                Inventory,
                Product,
            )
            .join(
                Product,
                Product.id
                == Inventory.product_id,
            )
        )

        if search:

            keyword = (
                f"%{search.strip()}%"
            )

            stmt = stmt.where(
                or_(
                    Product.name.ilike(
                        keyword
                    ),
                    Product.sku.ilike(
                        keyword
                    ),
                )
            )

        if low_stock_only:

            stmt = stmt.where(
                (
                    Inventory.available_quantity
                    - Inventory.reserved_quantity
                )
                <= Inventory.reorder_level
            )

        stmt = stmt.order_by(
            Product.name
        )

        result = await self.db.execute(
            stmt
        )

        return result.all()


    # -----------------------------------------
    # Single inventory
    # -----------------------------------------

    async def get_by_product_id(
        self,
        product_id: int,
    ) -> Inventory | None:

        result = await self.db.execute(
            select(Inventory)
            .where(
                Inventory.product_id
                == product_id
            )
        )

        return result.scalar_one_or_none()


    # -----------------------------------------
    # Product
    # -----------------------------------------

    async def get_product(
        self,
        product_id: int,
    ) -> Product | None:

        result = await self.db.execute(
            select(Product)
            .where(
                Product.id == product_id
            )
            .options(
                selectinload(
                    Product.images
                )
            )
        )

        return result.scalar_one_or_none()


    # -----------------------------------------
    # Transaction history
    # -----------------------------------------

    async def get_transactions(
        self,
        product_id: int,
        limit: int = 100,
    ):

        result = await self.db.execute(
            select(
                InventoryTransaction
            )
            .where(
                InventoryTransaction.product_id
                == product_id
            )
            .order_by(
                InventoryTransaction.created_at
                .desc()
            )
            .limit(limit)
        )

        return result.scalars().all()