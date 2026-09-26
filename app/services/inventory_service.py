# from decimal import Decimal

# from fastapi import HTTPException, status
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.inventory import Inventory
# from app.models.inventory_transaction import (
#     InventoryTransaction,
# )

import logging

from decimal import Decimal

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import (
    selectinload,
)


from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.inventory import Inventory

from app.models.inventory_transaction import (
    InventoryTransaction,
)

from app.models.product import Product

from app.services.broadcast_notification_service import (
    BroadcastNotificationService,
)

from sqlalchemy.orm import (
    selectinload,
)
import logging

from app.models.product import Product
from app.models.product_image import ProductImage

from app.services.broadcast_notification_service import (
    BroadcastNotificationService,
)

logger = logging.getLogger(__name__)

from app.models.product import Product


# class InventoryService:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):

class InventoryService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.broadcast_service = (
            BroadcastNotificationService(
                db
            )
        )
        
        
    
    
        # self.db = db

    async def add_stock(
        self,
        product_id: int,
        quantity: Decimal,
        user_id: int,
        note: str | None = None,
    ):

        # ======================================================
        # VALIDATE QUANTITY
        # ======================================================

        if quantity <= 0:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Quantity must be greater than zero"
                ),
            )


        # ======================================================
        # LOCK INVENTORY
        # ======================================================

        result = await self.db.execute(

            select(Inventory)
            .where(
                Inventory.product_id
                == product_id
            )
            .with_for_update()
        )


        inventory = (
            result.scalar_one_or_none()
        )


        if not inventory:

            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Inventory not found",
            )


        # ======================================================
        # CAPTURE OLD SELLABLE STOCK
        #
        # sellable = available - reserved
        # ======================================================

        old_sellable_quantity = (
            inventory.available_quantity
            - inventory.reserved_quantity
        )
        


        # ======================================================
        # ADD STOCK
        # ======================================================

        inventory.available_quantity += (
            quantity
        )


        # ======================================================
        # CALCULATE NEW SELLABLE STOCK
        # ======================================================

        new_sellable_quantity = (
            inventory.available_quantity
            - inventory.reserved_quantity
        )


        # ======================================================
        # DETECT BACK-IN-STOCK TRANSITION
        # ======================================================

        became_available = (
            old_sellable_quantity <= 0
            and new_sellable_quantity > 0
        )


        # ======================================================
        # INVENTORY TRANSACTION
        # ======================================================

        transaction = (
            InventoryTransaction(

                product_id=(
                    product_id
                ),

                transaction_type=(
                    "STOCK_IN"
                ),

                quantity=(
                    quantity
                ),

                note=note,

                created_by=(
                    user_id
                ),
            )
        )


        self.db.add(
            transaction
        )


        # ======================================================
        # COMMIT DATABASE FIRST
        # ======================================================

        await self.db.commit()


        await self.db.refresh(
            inventory
        )


        # ======================================================
        # SEND RESTOCK PUSH AFTER COMMIT
        # ======================================================

        if became_available:

            await self._send_restock_broadcast(
                product_id=product_id,
            )


        return inventory
    # async def add_stock(
    #     self,
    #     product_id: int,
    #     quantity: Decimal,
    #     user_id: int,
    #     note: str | None = None,
    # ):

    #     result = await self.db.execute(
    #         select(Inventory)
    #         .where(
    #             Inventory.product_id
    #             == product_id
    #         )
    #         .with_for_update()
    #     )

    #     inventory = (
    #         result.scalar_one_or_none()
    #     )

    #     if not inventory:

    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="Inventory not found",
    #         )

    #     inventory.available_quantity += (
    #         quantity
    #     )

    #     transaction = (
    #         InventoryTransaction(
    #             product_id=product_id,
    #             transaction_type="STOCK_IN",
    #             quantity=quantity,
    #             note=note,
    #             created_by=user_id,
    #         )
    #     )

    #     self.db.add(transaction)

    #     await self.db.commit()

    #     await self.db.refresh(inventory)

    #     return inventory
    
    
    
    # async def manual_adjustment(
    # self,
    # product_id: int,
    # direction: str,
    # quantity: Decimal,
    # user_id: int,
    # note: str,):
        

    #     result = await self.db.execute(
    #         select(Inventory)
    #         .where(
    #             Inventory.product_id
    #             == product_id
    #         )
    #         .with_for_update()
    #     )

    #     inventory = (
    #         result.scalar_one_or_none()
    #     )

    #     if not inventory:

    #         raise HTTPException(
    #             status_code=404,
    #             detail="Inventory not found",
    #         )

    #     if direction == "ADD":

    #         inventory.available_quantity += (
    #             quantity
    #         )

    #     elif direction == "REMOVE":

    #         remaining = (
    #             inventory.available_quantity
    #             - quantity
    #         )

    #         if remaining < inventory.reserved_quantity:

    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail=(
    #                     "Cannot remove stock because "
    #                     "some stock is reserved"
    #                 ),
    #             )

    #         inventory.available_quantity -= (
    #             quantity
    #         )

    #     else:

    #         raise HTTPException(
    #             status_code=400,
    #             detail="Invalid adjustment direction",
    #         )

    #     transaction = InventoryTransaction(
    #         product_id=product_id,
    #         transaction_type="MANUAL_ADJUSTMENT",
    #         quantity=quantity,
    #         note=f"{direction}: {note}",
    #         created_by=user_id,
    #     )

    #     self.db.add(transaction)

    #     await self.db.commit()
    #     await self.db.refresh(inventory)

    #     return inventory
    
        
    async def manual_adjustment(
        self,
        product_id: int,
        direction: str,
        quantity: Decimal,
        user_id: int,
        note: str,
    ):

        # ======================================================
        # NORMALIZE DIRECTION
        # ======================================================

        direction = (
            direction
            .strip()
            .upper()
        )


        # ======================================================
        # VALIDATE QUANTITY
        # ======================================================

        if quantity <= 0:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Quantity must be greater than zero"
                ),
            )


        # ======================================================
        # LOCK INVENTORY
        # ======================================================

        result = await self.db.execute(

            select(Inventory)
            .where(
                Inventory.product_id
                == product_id
            )
            .with_for_update()
        )


        inventory = (
            result.scalar_one_or_none()
        )


        if not inventory:

            raise HTTPException(
                status_code=404,
                detail="Inventory not found",
            )


        # ======================================================
        # OLD SELLABLE STOCK
        # ======================================================

        old_sellable_quantity = (
            inventory.available_quantity
            - inventory.reserved_quantity
        )


        # ======================================================
        # ADD
        # ======================================================

        if direction == "ADD":

            inventory.available_quantity += (
                quantity
            )


        # ======================================================
        # REMOVE
        # ======================================================

        elif direction == "REMOVE":

            remaining = (
                inventory.available_quantity
                - quantity
            )


            if (
                remaining
                < inventory.reserved_quantity
            ):

                raise HTTPException(
                    status_code=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                    detail=(
                        "Cannot remove stock because "
                        "some stock is reserved"
                    ),
                )


            inventory.available_quantity -= (
                quantity
            )


        else:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid adjustment direction"
                ),
            )


        # ======================================================
        # NEW SELLABLE STOCK
        # ======================================================

        new_sellable_quantity = (
            inventory.available_quantity
            - inventory.reserved_quantity
        )


        # ======================================================
        # BACK-IN-STOCK?
        #
        # Only ADD can produce a restock notification here.
        # ======================================================

        became_available = (
            direction == "ADD"
            and old_sellable_quantity <= 0
            and new_sellable_quantity > 0
        )


        # ======================================================
        # TRANSACTION
        # ======================================================

        transaction = (
            InventoryTransaction(

                product_id=(
                    product_id
                ),

                transaction_type=(
                    "MANUAL_ADJUSTMENT"
                ),

                quantity=(
                    quantity
                ),

                note=(
                    f"{direction}: {note}"
                ),

                created_by=(
                    user_id
                ),
            )
        )


        self.db.add(
            transaction
        )


        # ======================================================
        # COMMIT FIRST
        # ======================================================

        await self.db.commit()


        await self.db.refresh(
            inventory
        )


        # ======================================================
        # BROADCAST AFTER COMMIT
        # ======================================================

        if became_available:

            await self._send_restock_broadcast(
                product_id=product_id,
            )


        return inventory
    

    # async def _send_restock_broadcast(
    #     self,
    #     *,
    #     product_id: int,
    # ):
    #     """
    #     Send a public RESTOCK notification when
    #     a product changes from out-of-stock to
    #     sellable again.

    #     Push failure must never undo the inventory
    #     transaction.
    #     """

    #     try:

    #         # ==================================================
    #         # LOAD PRODUCT
    #         # ==================================================

    #         # result = await self.db.execute(

    #         #     select(Product)
    #         #     .where(
    #         #         Product.id
    #         #         == product_id
    #         #     )
    #         # )
    #         result = await self.db.execute(

    #             select(Product)
    #             .where(
    #                 Product.id
    #                 == product_id
    #             )
    #             .options(
    #                 selectinload(
    #                     Product.images
    #                 )
    #             )
    #         )

    #         product = (
    #             result.scalar_one_or_none()
    #         )


    #         if product is None:

    #             logger.warning(
    #                 (
    #                     "Restock push skipped because "
    #                     "product was not found. "
    #                     "product_id=%s"
    #                 ),
    #                 product_id,
    #             )
                
                
                
    #         image_url = None


    #         if product.images:

    #             primary_image = next(
    #                 (
    #                     image
    #                     for image in product.images
    #                     if image.is_primary
    #                 ),
    #                 None,
    #             )


    #             if primary_image is not None:

    #                 image_url = (
    #                     primary_image.image_url
    #                 )

    #             else:

    #                 image_url = (
    #                     product.images[0].image_url
    #                 )

    #             return None


    #         # ==================================================
    #         # DO NOT ADVERTISE INACTIVE PRODUCTS
    #         # ==================================================

    #         if not product.is_active:

    #             logger.info(
    #                 (
    #                     "Restock push skipped because "
    #                     "product is inactive. "
    #                     "product_id=%s"
    #                 ),
    #                 product_id,
    #             )

    #             return None


    #         # ==================================================
    #         # SEND BROADCAST
    #         # ==================================================

    #         result = (
    #             await self.broadcast_service.send(

    #                 notification_type=(
    #                     "RESTOCK"
    #                 ),

    #                 category=(
    #                     "PRODUCTS"
    #                 ),

    #                 title=(
    #                     "Back in Stock 🎉"
    #                 ),

    #                 message=(
    #                     f"{product.name} is back "
    #                     f"in stock on GramaGo. "
    #                     f"Tap to view the product."
    #                 ),

    #                 action=(
    #                     "OPEN_PRODUCT"
    #                 ),

    #                 reference_type=(
    #                     "PRODUCT"
    #                 ),

    #                 reference_id=(
    #                     product.id
    #                 ),
    #                 image_url=image_url,
    #             )
    #         )


    #         logger.info(
    #             (
    #                 "Restock broadcast processed. "
    #                 "product_id=%s "
    #                 "result=%s"
    #             ),
    #             product.id,
    #             result,
    #         )


    #         return result


    #     except Exception:

    #         logger.exception(
    #             (
    #                 "Failed to send restock "
    #                 "broadcast. product_id=%s"
    #             ),
    #             product_id,
    #         )


    #         return None







    async def _send_restock_broadcast(
        self,
        *,
        product_id: int,
    ):
        """
        Send RESTOCK notification when a product changes
        from unavailable to sellable.

        Product image is optional:
        - primary image preferred
        - otherwise first image
        - if no image exists, notification is still sent
        """

        try:

            # ==================================================
            # 1. LOAD PRODUCT
            # ==================================================

            result = await self.db.execute(

                select(Product)
                .where(
                    Product.id == product_id
                )
            )


            product = (
                result.scalar_one_or_none()
            )


            if product is None:

                logger.warning(
                    (
                        "RESTOCK notification skipped: "
                        "product not found. "
                        "product_id=%s"
                    ),
                    product_id,
                )

                return None


            # ==================================================
            # 2. ONLY ADVERTISE ACTIVE PRODUCTS
            # ==================================================

            if not product.is_active:

                logger.info(
                    (
                        "RESTOCK notification skipped: "
                        "product inactive. "
                        "product_id=%s"
                    ),
                    product_id,
                )

                return None


            # ==================================================
            # 3. GET PRIMARY PRODUCT IMAGE
            # ==================================================

            image_result = await self.db.execute(

                select(ProductImage)
                .where(
                    ProductImage.product_id
                    == product_id
                )
                .order_by(

                    # Primary image first
                    ProductImage.is_primary.desc(),

                    # Then normal product-image ordering
                    ProductImage.sort_order.asc(),

                    ProductImage.id.asc(),
                )
                .limit(1)
            )


            product_image = (
                image_result.scalar_one_or_none()
            )


            image_url = None


            if product_image is not None:

                image_url = (
                    product_image.image_url
                )


                if image_url:

                    image_url = (
                        image_url.strip()
                    )


                    if not image_url:

                        image_url = None


            # ==================================================
            # 4. DEBUG LOG
            # ==================================================

            logger.info(
                (
                    "Preparing RESTOCK broadcast. "
                    "product_id=%s "
                    "product_name=%s "
                    "image_available=%s"
                ),
                product.id,
                product.name,
                bool(image_url),
            )


            # ==================================================
            # 5. SEND BROADCAST
            # ==================================================

            push_result = (
                await self.broadcast_service.send(

                    notification_type=(
                        "RESTOCK"
                    ),

                    category=(
                        "PRODUCTS"
                    ),

                    title=(
                        "Back in Stock 🎉"
                    ),

                    message=(
                        f"{product.name} is back "
                        f"in stock on GramaGo. "
                        f"Tap to view the product."
                    ),

                    action=(
                        "OPEN_PRODUCT"
                    ),

                    reference_type=(
                        "PRODUCT"
                    ),

                    reference_id=(
                        product.id
                    ),

                    image_url=(
                        image_url
                    ),
                )
            )


            logger.info(
                (
                    "RESTOCK broadcast processed. "
                    "product_id=%s "
                    "image_available=%s "
                    "result=%s"
                ),
                product.id,
                bool(image_url),
                push_result,
            )


            return push_result


        except Exception:

            logger.exception(
                (
                    "RESTOCK broadcast failed. "
                    "product_id=%s"
                ),
                product_id,
            )


            # Do not raise.
            #
            # Inventory transaction has already
            # been committed successfully.
            return None
    
    
        
    async def mark_damaged(
    self,
    product_id: int,
    quantity: Decimal,
    user_id: int,
    note: str | None,
    ):

        result = await self.db.execute(
            select(Inventory)
            .where(
                Inventory.product_id
                == product_id
            )
            .with_for_update()
        )

        inventory = (
            result.scalar_one_or_none()
        )

        if not inventory:

            raise HTTPException(
                status_code=404,
                detail="Inventory not found",
            )

        if quantity <= 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Quantity must be greater than zero"
                ),
            )

        remaining = (
            inventory.available_quantity
            - quantity
        )

        if remaining < 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Damaged quantity exceeds "
                    "available stock"
                ),
            )

        if (
            remaining
            < inventory.reserved_quantity
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot mark this quantity as "
                    "damaged because some stock "
                    "is reserved for orders"
                ),
            )

        inventory.available_quantity -= (
            quantity
        )

        transaction = (
            InventoryTransaction(
                product_id=product_id,

                transaction_type=(
                    "DAMAGED"
                ),

                quantity=quantity,

                note=note,

                created_by=user_id,
            )
        )

        self.db.add(
            transaction
        )

        await self.db.commit()

        await self.db.refresh(
            inventory
        )

        return inventory

    # async def mark_damaged(
    #     self,
    #     product_id: int,
    #     quantity: Decimal,
    #     user_id: int,
    #     note: str | None,
    # ):

    #     result = await self.db.execute(
    #         select(Inventory)
    #         .where(
    #             Inventory.product_id
    #             == product_id
    #         )
    #         .with_for_update()
    #     )

    #     inventory = (
    #         result.scalar_one_or_none()
    #     )

    #     if not inventory:

    #         raise HTTPException(
    #             status_code=404,
    #             detail="Inventory not found",
    #         )

    #     remaining = (
    #         inventory.available_quantity
    #         - quantity
    #     )

    #     if remaining < inventory.reserved_quantity:

    #         raise HTTPException(
    #             status_code=400,
    #             detail=(
    #                 "Cannot mark this quantity as damaged "
    #                 "because stock is reserved"
    #             ),
    #         )

    #     inventory.available_quantity -= (
    #         quantity
    #     )

    #     transaction = InventoryTransaction(
    #         product_id=product_id,
    #         transaction_type="DAMAGED",
    #         quantity=quantity,
    #         note=note,
    #         created_by=user_id,
    #     )

    #     self.db.add(transaction)

    #     await self.db.commit()
    #     await self.db.refresh(inventory)

    #     return inventory
    
    



    async def set_reorder_level(
        self,
        product_id: int,
        reorder_level: Decimal,
    ):

        result = await self.db.execute(
            select(Inventory).where(
                Inventory.product_id
                == product_id
            )
        )

        inventory = (
            result.scalar_one_or_none()
        )

        if not inventory:

            raise HTTPException(
                status_code=404,
                detail="Inventory not found",
            )

        inventory.reorder_level = (
            reorder_level
        )

        await self.db.commit()
        await self.db.refresh(inventory)

        return inventory
        
        


    async def get_low_stock(
        self,
    ):

        result = await self.db.execute(
            select(
                Inventory,
                Product,
            )
            .join(
                Product,
                Product.id
                == Inventory.product_id,
            )
            .where(
                (
                    Inventory.available_quantity
                    - Inventory.reserved_quantity
                )
                <= Inventory.reorder_level
            )
            .order_by(
                Product.name
            )
        )

        return result.all()