# from fastapi import HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.inventory import Inventory
# from app.models.product import Product
# from app.repositories.category_repository import (
#     CategoryRepository,
# )
# from app.repositories.product_repository import (
#     ProductRepository,
# )
# from app.schemas.product import ProductCreate
# from app.utils.slug import generate_slug

# from app.schemas.product import (
#     ProductCreate,
#     ProductUpdate,
# )

# class ProductService:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db

#         self.products = ProductRepository(
#             db
#         )

#         self.categories = CategoryRepository(
#             db
#         )


#     async def create(
#         self,
#         data: ProductCreate,
#     ) -> Product:

#         category = (
#             await self.categories.get_by_id(
#                 data.category_id
#             )
#         )

#         if not category:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Category not found",
#             )

#         slug = generate_slug(
#             data.name
#         )

#         existing = (
#             await self.products.get_by_slug(
#                 slug
#             )
#         )

#         if existing:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="Product already exists",
#             )

#         if (
#             data.discount_price is not None
#             and data.discount_price > data.price
#         ):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Discount price cannot be "
#                     "greater than regular price"
#                 ),
#             )
            
        
        
#         product = Product(
#             category_id=data.category_id,
#             name=data.name.strip(),
#             slug=slug,
#             sku=None,
#             description=data.description,
#             price=data.price,
#             discount_price=data.discount_price,
#             unit=data.unit.upper(),
#             unit_value=data.unit_value,
#             min_order_qty=data.min_order_qty,
#             max_order_qty=data.max_order_qty,
#             is_featured=data.is_featured,
#         )

#         self.db.add(product)

#         await self.db.flush()


#         category_name = category.name.strip().upper()

#         category_short = category_name[:3]

#         product_name = (
#             data.name.strip()
#             .upper()
#             .replace(" ", "-")
#         )

#         product.sku = (
#             f"{category_short}-"
#             f"{product_name}-"
#             f"{product.id:03d}"
#         )


#         inventory = Inventory(
#             product_id=product.id,
#             available_quantity=0,
#             reserved_quantity=0,
#             reorder_level=0,
#         )

#         self.db.add(inventory)

#         await self.db.commit()

#         await self.db.refresh(product)

#         return product

#     async def update(
#     self,
#     product_id: int,
#     data: ProductUpdate,
# ) -> Product:

#         product = await self.products.get_by_id(
#             product_id
#         )

#         if not product:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Product not found",
#             )


#         # -----------------------------------------
#         # Update Category
#         # -----------------------------------------

#         if data.category_id is not None:

#             category = await self.categories.get_by_id(
#                 data.category_id
#             )

#             if not category:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="Category not found",
#                 )

#             product.category_id = data.category_id


#         # -----------------------------------------
#         # Update Product Name
#         # -----------------------------------------

#         if data.name is not None:

#             slug = generate_slug(
#                 data.name
#             )

#             existing = await self.products.get_by_slug(
#                 slug
#             )

#             if (
#                 existing
#                 and existing.id != product.id
#             ):
#                 raise HTTPException(
#                     status_code=status.HTTP_409_CONFLICT,
#                     detail="Product name already exists",
#                 )

#             product.name = data.name.strip()
#             product.slug = slug


#         # -----------------------------------------
#         # Do NOT manually update SKU
#         # SKU is managed automatically by backend
#         # -----------------------------------------


#         # -----------------------------------------
#         # Update Description
#         # -----------------------------------------

#         if data.description is not None:
#             product.description = data.description


#         # -----------------------------------------
#         # Update Price
#         # -----------------------------------------

#         if data.price is not None:
#             product.price = data.price


#         if "discount_price" in data.model_fields_set:

#             product.discount_price = (
#                 data.discount_price
#             )


#         # -----------------------------------------
#         # Update Unit
#         # -----------------------------------------

#         if data.unit is not None:
#             product.unit = data.unit.upper()


#         if data.unit_value is not None:
#             product.unit_value = data.unit_value


#         # -----------------------------------------
#         # Update Order Quantity Limits
#         # -----------------------------------------

#         if data.min_order_qty is not None:

#             product.min_order_qty = (
#                 data.min_order_qty
#             )


#         if "max_order_qty" in data.model_fields_set:

#             product.max_order_qty = (
#                 data.max_order_qty
#             )


#         # -----------------------------------------
#         # Update Status
#         # -----------------------------------------

#         if data.is_active is not None:
#             product.is_active = data.is_active


#         if data.is_featured is not None:

#             product.is_featured = (
#                 data.is_featured
#             )


#         # -----------------------------------------
#         # Validate Discount
#         # -----------------------------------------

#         if (
#             product.discount_price is not None
#             and product.discount_price
#             > product.price
#         ):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Discount price cannot be "
#                     "greater than product price"
#                 ),
#             )


#         # -----------------------------------------
#         # Validate Quantity Limits
#         # -----------------------------------------

#         if (
#             product.max_order_qty is not None
#             and product.max_order_qty
#             < product.min_order_qty
#         ):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Maximum order quantity cannot "
#                     "be less than minimum quantity"
#                 ),
#             )


#         # -----------------------------------------
#         # Generate SKU if missing
#         # -----------------------------------------

#         if not product.sku:

#             category = await self.categories.get_by_id(
#                 product.category_id
#             )

#             if not category:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="Category not found",
#                 )


#             category_name = (
#                 category.name
#                 .strip()
#                 .upper()
#             )

#             category_short = (
#                 category_name[:3]
#             )


#             product_name = (
#                 product.name
#                 .strip()
#                 .upper()
#                 .replace(" ", "-")
#             )


#             product.sku = (
#                 f"{category_short}-"
#                 f"{product_name}-"
#                 f"{product.id:03d}"
#             )


#         # -----------------------------------------
#         # Save Changes
#         # -----------------------------------------

#         await self.db.commit()

#         await self.db.refresh(
#             product
#         )

#         return product


#     async def deactivate(
#         self,
#         product_id: int,
#     ) -> Product:

#         product = await self.products.get_by_id(
#             product_id
#         )

#         if not product:

#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Product not found",
#             )

#         product.is_active = False

#         await self.db.commit()
#         await self.db.refresh(product)

#         return product








import logging
from decimal import Decimal

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.inventory import Inventory
from app.models.product import Product

from app.repositories.category_repository import (
    CategoryRepository,
)
from app.repositories.product_repository import (
    ProductRepository,
)

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
)

from app.services.broadcast_notification_service import (
    BroadcastNotificationService,
)

from app.utils.slug import generate_slug


logger = logging.getLogger(__name__)


class ProductService:

    # ==========================================================
    # CONSTRUCTOR
    # ==========================================================

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.products = (
            ProductRepository(db)
        )

        self.categories = (
            CategoryRepository(db)
        )

        self.broadcast_service = (
            BroadcastNotificationService(
                db
            )
        )


    # ==========================================================
    # EFFECTIVE CUSTOMER PRICE
    # ==========================================================

    @staticmethod
    def _effective_price(
        price: Decimal,
        discount_price: Decimal | None,
    ) -> Decimal:
        """
        Return the actual price visible/payable
        by the customer.

        Example:

        price = 100
        discount = 80

        effective price = 80
        """

        if (
            discount_price is not None
            and discount_price < price
        ):
            return discount_price

        return price




    async def _get_product_image_url(
        self,
        product_id: int,
    ) -> str | None:

        product = (
            await self.products.get_by_id(
                product_id,
                include_relations=True,
            )
        )


        if (
            product is None
            or not product.images
        ):
            return None


        # Prefer primary image.
        primary_image = next(
            (
                image
                for image in product.images
                if image.is_primary
            ),
            None,
        )


        if primary_image is not None:

            return (
                primary_image.image_url
            )


        # Fallback to first image.
        return (
            product.images[0].image_url
        )
    
    # ==========================================================
    # CREATE PRODUCT
    # ==========================================================

    async def create(
        self,
        data: ProductCreate,
    ) -> Product:

        # ------------------------------------------------------
        # 1. Validate category
        # ------------------------------------------------------

        category = (
            await self.categories.get_by_id(
                data.category_id
            )
        )


        if not category:

            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Category not found",
            )


        # ------------------------------------------------------
        # 2. Generate slug
        # ------------------------------------------------------

        slug = generate_slug(
            data.name
        )


        existing = (
            await self.products.get_by_slug(
                slug
            )
        )


        if existing:

            raise HTTPException(
                status_code=(
                    status.HTTP_409_CONFLICT
                ),
                detail="Product already exists",
            )


        # ------------------------------------------------------
        # 3. Validate discount
        # ------------------------------------------------------

        if (
            data.discount_price is not None
            and data.discount_price
            > data.price
        ):

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Discount price cannot be "
                    "greater than regular price"
                ),
            )


        # ------------------------------------------------------
        # 4. Create product
        # ------------------------------------------------------

        product = Product(

            category_id=(
                data.category_id
            ),

            name=(
                data.name.strip()
            ),

            slug=slug,

            sku=None,

            description=(
                data.description
            ),

            price=(
                data.price
            ),

            discount_price=(
                data.discount_price
            ),

            unit=(
                data.unit.upper()
            ),

            unit_value=(
                data.unit_value
            ),

            min_order_qty=(
                data.min_order_qty
            ),

            max_order_qty=(
                data.max_order_qty
            ),

            is_featured=(
                data.is_featured
            ),
        )


        self.db.add(
            product
        )


        # ------------------------------------------------------
        # 5. Flush to generate product ID
        # ------------------------------------------------------

        await self.db.flush()


        # ------------------------------------------------------
        # 6. Generate SKU
        # ------------------------------------------------------

        category_name = (
            category.name
            .strip()
            .upper()
        )


        category_short = (
            category_name[:3]
        )


        product_name = (
            data.name
            .strip()
            .upper()
            .replace(
                " ",
                "-",
            )
        )


        product.sku = (
            f"{category_short}-"
            f"{product_name}-"
            f"{product.id:03d}"
        )


        # ------------------------------------------------------
        # 7. Create inventory
        # ------------------------------------------------------

        inventory = Inventory(

            product_id=(
                product.id
            ),

            available_quantity=0,

            reserved_quantity=0,

            reorder_level=0,
        )


        self.db.add(
            inventory
        )


        # ------------------------------------------------------
        # 8. Commit product FIRST
        # ------------------------------------------------------

        await self.db.commit()


        await self.db.refresh(
            product
        )


        # ------------------------------------------------------
        # 9. Broadcast NEW PRODUCT
        # ------------------------------------------------------

        # await self._send_new_product_broadcast(
        #     product
        # )


        return product


    # ==========================================================
    # UPDATE PRODUCT
    # ==========================================================

    async def update(
        self,
        product_id: int,
        data: ProductUpdate,
    ) -> Product:

        product = (
            await self.products.get_by_id(
                product_id
            )
        )


        if not product:

            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Product not found",
            )


        # ======================================================
        # IMPORTANT:
        # CAPTURE OLD CUSTOMER PRICE BEFORE CHANGING PRODUCT
        # ======================================================

        old_price = product.price

        old_discount_price = (
            product.discount_price
        )


        old_effective_price = (
            self._effective_price(
                old_price,
                old_discount_price,
            )
        )


        # Also remember old active status.
        old_is_active = (
            product.is_active
        )


        # ------------------------------------------------------
        # Update Category
        # ------------------------------------------------------

        if data.category_id is not None:

            category = (
                await self.categories.get_by_id(
                    data.category_id
                )
            )


            if not category:

                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail="Category not found",
                )


            product.category_id = (
                data.category_id
            )


        # ------------------------------------------------------
        # Update Product Name
        # ------------------------------------------------------

        if data.name is not None:

            slug = generate_slug(
                data.name
            )


            existing = (
                await self.products.get_by_slug(
                    slug
                )
            )


            if (
                existing
                and existing.id
                != product.id
            ):

                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "Product name already exists"
                    ),
                )


            product.name = (
                data.name.strip()
            )


            product.slug = (
                slug
            )


        # ------------------------------------------------------
        # SKU is backend managed
        # ------------------------------------------------------


        # ------------------------------------------------------
        # Update Description
        # ------------------------------------------------------

        if data.description is not None:

            product.description = (
                data.description
            )


        # ------------------------------------------------------
        # Update Regular Price
        # ------------------------------------------------------

        if data.price is not None:

            product.price = (
                data.price
            )


        # ------------------------------------------------------
        # Update Discount Price
        #
        # Important:
        # model_fields_set allows:
        #
        # discount_price = null
        #
        # which removes an existing discount.
        # ------------------------------------------------------

        if (
            "discount_price"
            in data.model_fields_set
        ):

            product.discount_price = (
                data.discount_price
            )


        # ------------------------------------------------------
        # Update Unit
        # ------------------------------------------------------

        if data.unit is not None:

            product.unit = (
                data.unit.upper()
            )


        if data.unit_value is not None:

            product.unit_value = (
                data.unit_value
            )


        # ------------------------------------------------------
        # Update Quantity Limits
        # ------------------------------------------------------

        if data.min_order_qty is not None:

            product.min_order_qty = (
                data.min_order_qty
            )


        if (
            "max_order_qty"
            in data.model_fields_set
        ):

            product.max_order_qty = (
                data.max_order_qty
            )


        # ------------------------------------------------------
        # Update Status
        # ------------------------------------------------------

        if data.is_active is not None:

            product.is_active = (
                data.is_active
            )


        if data.is_featured is not None:

            product.is_featured = (
                data.is_featured
            )


        # ------------------------------------------------------
        # Validate Discount
        # ------------------------------------------------------

        if (
            product.discount_price is not None
            and product.discount_price
            > product.price
        ):

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Discount price cannot be "
                    "greater than product price"
                ),
            )


        # ------------------------------------------------------
        # Validate Quantity Limits
        # ------------------------------------------------------

        if (
            product.max_order_qty
            is not None

            and product.max_order_qty
            < product.min_order_qty
        ):

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Maximum order quantity cannot "
                    "be less than minimum quantity"
                ),
            )


        # ------------------------------------------------------
        # Generate SKU if missing
        # ------------------------------------------------------

        if not product.sku:

            category = (
                await self.categories.get_by_id(
                    product.category_id
                )
            )


            if not category:

                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail="Category not found",
                )


            category_name = (
                category.name
                .strip()
                .upper()
            )


            category_short = (
                category_name[:3]
            )


            product_name = (
                product.name
                .strip()
                .upper()
                .replace(
                    " ",
                    "-",
                )
            )


            product.sku = (
                f"{category_short}-"
                f"{product_name}-"
                f"{product.id:03d}"
            )


        # ======================================================
        # CALCULATE NEW CUSTOMER PRICE
        # ======================================================

        new_effective_price = (
            self._effective_price(
                product.price,
                product.discount_price,
            )
        )


        # ------------------------------------------------------
        # Detect whether customer-visible price changed
        # ------------------------------------------------------

        price_changed = (
            old_effective_price
            != new_effective_price
        )


        # ------------------------------------------------------
        # Detect inactive -> active
        # ------------------------------------------------------

        became_active = (
            old_is_active is False
            and product.is_active is True
        )


        # ------------------------------------------------------
        # Save database changes FIRST
        # ------------------------------------------------------

        await self.db.commit()


        await self.db.refresh(
            product
        )


        # ======================================================
        # SEND BROADCASTS AFTER COMMIT
        # ======================================================

        # ------------------------------------------------------
        # Product became active again
        # ------------------------------------------------------

        if became_active:

            await self.send_new_product_broadcast(
                product
            )


        # ------------------------------------------------------
        # Customer price changed
        # ------------------------------------------------------

        if (
            price_changed
            and product.is_active
        ):

            await self._send_price_update_broadcast(
                product=product,

                old_price=(
                    old_effective_price
                ),

                new_price=(
                    new_effective_price
                ),
            )


        return product


    # ==========================================================
    # NEW PRODUCT BROADCAST
    # ==========================================================

    # async def _send_new_product_broadcast(
    #     self,
    #     product: Product,
    # ):
    #     """
    #     Send public push notification for a
    #     newly-added/activated product.

    #     Push failure must not break product creation.
    #     """

    #     try:

    #         await self.broadcast_service.send(

    #             notification_type=(
    #                 "NEW_PRODUCT"
    #             ),

    #             category=(
    #                 "PRODUCTS"
    #             ),

    #             title=(
    #                 "New Product Added 🛍️"
    #             ),

    #             message=(
    #                 f"{product.name} is now "
    #                 f"available on GramaGo."
    #             ),

    #             action=(
    #                 "OPEN_PRODUCT"
    #             ),

    #             reference_type=(
    #                 "PRODUCT"
    #             ),

    #             reference_id=(
    #                 product.id
    #             ),
    #         )


    #         logger.info(
    #             (
    #                 "New-product broadcast sent. "
    #                 "product_id=%s"
    #             ),
    #             product.id,
    #         )


    #     except Exception:

    #         logger.exception(
    #             (
    #                 "Failed to send new-product "
    #                 "broadcast. product_id=%s"
    #             ),
    #             product.id,
    #         )


    async def send_new_product_broadcast(
        self,
        product: Product,
    ):
        try:

            image_url = (
                await self._get_product_image_url(
                    product.id
                )
            )


            await self.broadcast_service.send(

                notification_type=(
                    "NEW_PRODUCT"
                ),

                category=(
                    "PRODUCTS"
                ),

                title=(
                    "New Product Added 🛍️"
                ),

                message=(
                    f"{product.name} is now "
                    f"available on GramaGo."
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


            logger.info(
                (
                    "New-product broadcast sent. "
                    "product_id=%s"
                ),
                product.id,
            )


        except Exception:

            logger.exception(
                (
                    "Failed to send new-product "
                    "broadcast. product_id=%s"
                ),
                product.id,
            )

    # ==========================================================
    # PRICE UPDATE BROADCAST
    # ==========================================================

    async def _send_price_update_broadcast(
        self,
        *,
        product: Product,
        old_price: Decimal,
        new_price: Decimal,
    ):
        """
        Send notification whenever the actual
        customer-visible product price changes.
        """

        try:

            # --------------------------------------------------
            # Price went DOWN
            # --------------------------------------------------

            if new_price < old_price:

                notification_type = (
                    "PRICE_DROP"
                )

                title = (
                    "Price Drop 🔥"
                )

                message = (
                    f"{product.name} price dropped "
                    f"from ₹{self._format_price(old_price)} "
                    f"to ₹{self._format_price(new_price)}. "
                    f"Tap to view the product."
                )


            # --------------------------------------------------
            # Price went UP
            # --------------------------------------------------

            else:

                notification_type = (
                    "PRICE_UPDATED"
                )

                title = (
                    "Price Updated"
                )

                message = (
                    f"{product.name} price changed "
                    f"from ₹{self._format_price(old_price)} "
                    f"to ₹{self._format_price(new_price)}. "
                    f"Tap to view the product."
                )
                
                
            image_url = (
                await self._get_product_image_url(
                    product.id
                )
            )

            await self.broadcast_service.send(

                notification_type=(
                    notification_type
                ),

                category=(
                    "PRICE_ALERTS"
                ),

                title=title,

                message=message,

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


            logger.info(
                (
                    "Product price broadcast sent. "
                    "product_id=%s "
                    "old_price=%s "
                    "new_price=%s"
                ),
                product.id,
                old_price,
                new_price,
            )


        except Exception:

            logger.exception(
                (
                    "Failed to send product-price "
                    "broadcast. product_id=%s"
                ),
                product.id,
            )


    # ==========================================================
    # FORMAT PRICE
    # ==========================================================

    @staticmethod
    def _format_price(
        value: Decimal,
    ) -> str:

        """
        ₹100.00 -> 100
        ₹99.50  -> 99.50
        """

        decimal_value = (
            Decimal(value)
        )


        if (
            decimal_value
            == decimal_value.to_integral()
        ):

            return str(
                int(decimal_value)
            )


        return format(
            decimal_value,
            ".2f",
        ).rstrip(
            "0"
        ).rstrip(
            "."
        )


    # ==========================================================
    # DEACTIVATE PRODUCT
    # ==========================================================

    async def deactivate(
        self,
        product_id: int,
    ) -> Product:

        product = (
            await self.products.get_by_id(
                product_id
            )
        )


        if not product:

            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Product not found",
            )


        product.is_active = False


        await self.db.commit()


        await self.db.refresh(
            product
        )


        return product