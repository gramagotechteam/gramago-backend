# from decimal import Decimal



# from app.services.notification_service import (
#     NotificationService,
# )

# import logging

# from fastapi import (
#     HTTPException,
#     status,
# )
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload

# from app.models.cart import Cart
# from app.models.inventory import Inventory
# from app.models.inventory_transaction import (
#     InventoryTransaction,
# )
# from app.models.order import Order
# from app.models.order_item import OrderItem
# from app.models.order_status_history import (
#     OrderStatusHistory,
# )
# from app.models.payment import Payment
# from app.models.product import Product
# from app.repositories.address_repository import (
#     AddressRepository,
# )
# from app.utils.order_number import (
#     generate_order_number,
# )

# from app.services.commerce_pricing_service import (
#     CommercePricingService,
# )

# from app.services.notification_service import (
#     NotificationService,
# )



# logger = logging.getLogger(__name__)


# class CheckoutService:

#     # DELIVERY_FEE = Decimal("20.00")

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db

#         self.addresses = AddressRepository(
#             db
#         )
        
#         self.notification_service = (
#     NotificationService(db)
# )


#     async def create_order(
#         self,
#         user_id: int,
#         address_id: int,
#         customer_note: str | None,
#     ) -> Order:

#         try:

#             # =================================
#             # 1. Validate delivery address
#             # =================================

#             address = (
#                 await self.addresses
#                 .get_user_address(
#                     address_id,
#                     user_id,
#                 )
#             )

#             if not address:

#                 raise HTTPException(
#                     status_code=404,
#                     detail=(
#                         "Delivery address not found"
#                     ),
#                 )


#             # =================================
#             # 2. Lock active cart
#             # =================================

#             result = await self.db.execute(
#                 select(Cart)
#                 .where(
#                     Cart.user_id == user_id,
#                     Cart.status == "ACTIVE",
#                 )
#                 .options(
#                     selectinload(
#                         Cart.items
#                     )
#                 )
#                 .with_for_update()
#             )

#             cart = (
#                 result.scalar_one_or_none()
#             )

#             if not cart:

#                 raise HTTPException(
#                     status_code=400,
#                     detail="Active cart not found",
#                 )

#             if not cart.items:

#                 raise HTTPException(
#                     status_code=400,
#                     detail="Cart is empty",
#                 )


#             # =================================
#             # 3. Validate cart products
#             # =================================

#             subtotal = Decimal("0.00")

#             validated_items = []


#             for cart_item in cart.items:

#                 # -----------------------------
#                 # Product
#                 # -----------------------------

#                 product_result = (
#                     await self.db.execute(
#                         select(Product)
#                         .where(
#                             Product.id
#                             == cart_item.product_id
#                         )
#                     )
#                 )

#                 product = (
#                     product_result
#                     .scalar_one_or_none()
#                 )

#                 if (
#                     not product
#                     or not product.is_active
#                 ):

#                     raise HTTPException(
#                         status_code=400,
#                         detail=(
#                             "One or more products "
#                             "are unavailable"
#                         ),
#                     )


#                 # -----------------------------
#                 # Lock inventory
#                 # -----------------------------

#                 inventory_result = (
#                     await self.db.execute(
#                         select(Inventory)
#                         .where(
#                             Inventory.product_id
#                             == product.id
#                         )
#                         .with_for_update()
#                     )
#                 )

#                 inventory = (
#                     inventory_result
#                     .scalar_one_or_none()
#                 )

#                 if not inventory:

#                     raise HTTPException(
#                         status_code=400,
#                         detail=(
#                             f"Inventory unavailable "
#                             f"for {product.name}"
#                         ),
#                     )


#                 # -----------------------------
#                 # Calculate sellable stock
#                 # -----------------------------

#                 sellable = (
#                     inventory.available_quantity
#                     - inventory.reserved_quantity
#                 )

#                 if (
#                     cart_item.quantity
#                     > sellable
#                 ):

#                     raise HTTPException(
#                         status_code=400,
#                         detail=(
#                             f"Only {sellable} "
#                             f"{product.unit} of "
#                             f"{product.name} "
#                             f"is available"
#                         ),
#                     )


#                 # -----------------------------
#                 # Minimum quantity
#                 # -----------------------------

#                 if (
#                     cart_item.quantity
#                     < product.min_order_qty
#                 ):

#                     raise HTTPException(
#                         status_code=400,
#                         detail=(
#                             f"Minimum order quantity "
#                             f"for {product.name} is "
#                             f"{product.min_order_qty}"
#                         ),
#                     )


#                 # -----------------------------
#                 # Maximum quantity
#                 # -----------------------------

#                 if (
#                     product.max_order_qty
#                     is not None
#                     and cart_item.quantity
#                     > product.max_order_qty
#                 ):

#                     raise HTTPException(
#                         status_code=400,
#                         detail=(
#                             f"Maximum order quantity "
#                             f"for {product.name} is "
#                             f"{product.max_order_qty}"
#                         ),
#                     )


#                 # -----------------------------
#                 # Latest price
#                 # -----------------------------

#                 effective_price = (
#                     product.discount_price
#                     if product.discount_price
#                     is not None
#                     else product.price
#                 )


#                 line_total = (
#                     effective_price
#                     * cart_item.quantity
#                 )

#                 subtotal += line_total
                
#                 pricing_service = (
#     CommercePricingService(
#         self.db
#     )
# )

#                 pricing = await pricing_service.calculate(
#                     subtotal=subtotal,
#                     discount=Decimal("0.00"),
#                 )
                
#                 subtotal = pricing["subtotal"]

#                 delivery_fee = pricing[
#                     "delivery_fee"
#                 ]

#                 discount = pricing[
#                     "discount"
#                 ]

#                 total = pricing[
#                     "total"
#                 ]


#                 validated_items.append(
#                     (
#                         cart_item,
#                         product,
#                         inventory,
#                         effective_price,
#                         line_total,
#                     )
#                 )


#             # =================================
#             # 4. Calculate final amount
#             # =================================

#             delivery_fee = (
#                 self.DELIVERY_FEE
#             )

#             discount_amount = (
#                 Decimal("0.00")
#             )

#             total_amount = (
#                 subtotal
#                 + delivery_fee
#                 - discount_amount
#             )


#             # =================================
#             # 5. Create Order
#             # =================================

#             order = Order(

#                 order_number=(
#                     generate_order_number()
#                 ),

#                 user_id=user_id,

#                 source_address_id=(
#                     address.id
#                 ),

#                 order_status="PLACED",

#                 payment_status="PENDING",

#                 subtotal=subtotal,

#                 delivery_fee=delivery_fee,

#                 discount_amount=(
#                     discount_amount
#                 ),

#                 total_amount=(
#                     total_amount
#                 ),

#                 customer_note=(
#                     customer_note
#                 ),


#                 # -----------------------------
#                 # Delivery address snapshot
#                 # -----------------------------

#                 delivery_full_name=(
#                     address.full_name
#                 ),

#                 delivery_phone=(
#                     address.phone
#                 ),

#                 delivery_house_no=(
#                     address.house_no
#                 ),

#                 delivery_street=(
#                     address.street
#                 ),

#                 delivery_village_town=(
#                     address.village_town
#                 ),

#                 delivery_mandal=(
#                     address.mandal
#                 ),

#                 delivery_district=(
#                     address.district
#                 ),

#                 delivery_state=(
#                     address.state
#                 ),

#                 delivery_pincode=(
#                     address.pincode
#                 ),

#                 delivery_landmark=(
#                     address.landmark
#                 ),

#                 delivery_latitude=(
#                     address.latitude
#                 ),

#                 delivery_longitude=(
#                     address.longitude
#                 ),
#             )


#             self.db.add(order)

#             # We need order.id before creating
#             # order items/payment/history.
#             await self.db.flush()


#             # =================================
#             # 6. Create Order Items
#             #    + Reserve stock
#             # =================================

#             for (
#                 cart_item,
#                 product,
#                 inventory,
#                 effective_price,
#                 line_total,
#             ) in validated_items:


#                 original_price_total = (
#                     product.price
#                     * cart_item.quantity
#                 )


#                 item_discount = (
#                     original_price_total
#                     - line_total
#                 )


#                 order_item = OrderItem(

#                     order_id=(
#                         order.id
#                     ),

#                     product_id=(
#                         product.id
#                     ),

#                     product_name=(
#                         product.name
#                     ),

#                     product_sku=(
#                         product.sku
#                     ),

#                     unit=(
#                         product.unit
#                     ),

#                     unit_value=(
#                         product.unit_value
#                     ),

#                     quantity=(
#                         cart_item.quantity
#                     ),

#                     unit_price=(
#                         effective_price
#                     ),

#                     discount_amount=(
#                         item_discount
#                     ),

#                     line_total=(
#                         line_total
#                     ),
#                 )


#                 self.db.add(
#                     order_item
#                 )


#                 # -----------------------------
#                 # Reserve inventory
#                 # -----------------------------

#                 inventory.reserved_quantity += (
#                     cart_item.quantity
#                 )


#                 # -----------------------------
#                 # Inventory ledger
#                 # -----------------------------

#                 inventory_transaction = (
#                     InventoryTransaction(

#                         product_id=(
#                             product.id
#                         ),

#                         transaction_type=(
#                             "ORDER_RESERVED"
#                         ),

#                         quantity=(
#                             cart_item.quantity
#                         ),

#                         reference_type=(
#                             "ORDER"
#                         ),

#                         reference_id=(
#                             order.id
#                         ),

#                         note=(
#                             f"Reserved for "
#                             f"{order.order_number}"
#                         ),

#                         created_by=(
#                             user_id
#                         ),
#                     )
#                 )


#                 self.db.add(
#                     inventory_transaction
#                 )


#             # =================================
#             # 7. COD Payment
#             # =================================

#             payment = Payment(

#                 order_id=(
#                     order.id
#                 ),

#                 method="COD",

#                 status="PENDING",

#                 amount=(
#                     total_amount
#                 ),

#                 provider=None,

#                 transaction_id=None,
#             )


#             self.db.add(
#                 payment
#             )


#             # =================================
#             # 8. Initial status history
#             # =================================

#             status_history = (
#                 OrderStatusHistory(

#                     order_id=(
#                         order.id
#                     ),

#                     from_status=None,

#                     to_status="PLACED",

#                     changed_by=(
#                         user_id
#                     ),

#                     note=(
#                         "Order placed by customer"
#                     ),
#                 )
#             )


#             self.db.add(
#                 status_history
#             )


#             # =================================
#             # 9. Convert current cart
#             # =================================

#             cart.status = (
#                 "CONVERTED"
#             )


#             # =================================
#             # 10. Commit EVERYTHING
#             # =================================
            
#             await self.notification_service.create(

#     user_id=user_id,

#     notification_type="ORDER_PLACED",

#     title="Order Placed ✅",

#     # message=(
#     #     f"Your order "
#     #     f"{order.order_number} "
#     #     f"has been placed successfully."
#     # ),
#     message=(
#         f"Your order {order.order_number} "
#         f"has been placed successfully."
#     ),
#     action="OPEN_ORDER",

#     reference_type="ORDER",

#     reference_id=order.id,

#     # reference_type="ORDER",

#     # reference_id=order.id,
# )

#             await self.db.commit()
            
            
# #             await self.db.refresh(
# #     notification
# # )

# #             await notification_service.dispatch(
# #     notification
# # )


#             # =================================
#             # 11. Refresh order
#             # =================================

#             await self.db.refresh(
#                 order
#             )


#             return order


#         except HTTPException:

#             await self.db.rollback()

#             raise


#         except Exception as exc:

#             await self.db.rollback()

#             # IMPORTANT while developing:
#             # show actual error in terminal.
#             logger.exception(
#                 "Checkout failed"
#             )

#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=(
#                     "Unable to place order"
#                 ),
#             ) from exc










from decimal import Decimal
import logging

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.inventory import Inventory
from app.models.inventory_transaction import (
    InventoryTransaction,
)
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_status_history import (
    OrderStatusHistory,
)
from app.models.payment import Payment
from app.models.product import Product

from app.repositories.address_repository import (
    AddressRepository,
)

from app.services.commerce_pricing_service import (
    CommercePricingService,
)
from app.services.notification_service import (
    NotificationService,
)

from app.utils.order_number import (
    generate_order_number,
)


logger = logging.getLogger(
    __name__
)


class CheckoutService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.addresses = (
            AddressRepository(
                db
            )
        )

        self.notification_service = (
            NotificationService(
                db
            )
        )

        self.pricing_service = (
            CommercePricingService(
                db
            )
        )

    # =========================================================
    # CREATE ORDER
    # =========================================================

    async def create_order(
        self,
        user_id: int,
        address_id: int,
        customer_note: str | None,
    ) -> Order:

        try:

            # =================================================
            # 1. VALIDATE DELIVERY ADDRESS
            # =================================================

            address = (
                await self.addresses
                .get_user_address(
                    address_id,
                    user_id,
                )
            )

            if not address:

                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail=(
                        "Delivery address not found"
                    ),
                )

            # =================================================
            # 2. LOCK ACTIVE CART
            # =================================================

            result = await self.db.execute(
                select(
                    Cart
                )
                .where(
                    Cart.user_id
                    == user_id,

                    Cart.status
                    == "ACTIVE",
                )
                .options(
                    selectinload(
                        Cart.items
                    )
                )
                .with_for_update()
            )

            cart = (
                result.scalar_one_or_none()
            )

            if not cart:

                raise HTTPException(
                    status_code=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                    detail=(
                        "Active cart not found"
                    ),
                )

            if not cart.items:

                raise HTTPException(
                    status_code=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                    detail=(
                        "Cart is empty"
                    ),
                )

            # =================================================
            # 3. VALIDATE CART PRODUCTS
            # =================================================

            subtotal = Decimal(
                "0.00"
            )

            validated_items = []

            for cart_item in cart.items:

                # ---------------------------------------------
                # PRODUCT
                # ---------------------------------------------

                product_result = (
                    await self.db.execute(
                        select(
                            Product
                        )
                        .where(
                            Product.id
                            == cart_item.product_id
                        )
                    )
                )

                product = (
                    product_result
                    .scalar_one_or_none()
                )

                if (
                    not product
                    or
                    not product.is_active
                ):

                    raise HTTPException(
                        status_code=(
                            status.HTTP_400_BAD_REQUEST
                        ),
                        detail=(
                            "One or more products "
                            "are unavailable"
                        ),
                    )

                # ---------------------------------------------
                # LOCK INVENTORY
                # ---------------------------------------------

                inventory_result = (
                    await self.db.execute(
                        select(
                            Inventory
                        )
                        .where(
                            Inventory.product_id
                            == product.id
                        )
                        .with_for_update()
                    )
                )

                inventory = (
                    inventory_result
                    .scalar_one_or_none()
                )

                if not inventory:

                    raise HTTPException(
                        status_code=(
                            status.HTTP_400_BAD_REQUEST
                        ),
                        detail=(
                            f"Inventory unavailable "
                            f"for {product.name}"
                        ),
                    )

                # ---------------------------------------------
                # SELLABLE STOCK
                # ---------------------------------------------

                sellable = (
                    inventory.available_quantity
                    -
                    inventory.reserved_quantity
                )

                if (
                    cart_item.quantity
                    > sellable
                ):

                    raise HTTPException(
                        status_code=(
                            status.HTTP_400_BAD_REQUEST
                        ),
                        detail=(
                            f"Only {sellable} "
                            f"{product.unit} of "
                            f"{product.name} "
                            f"is available"
                        ),
                    )

                # ---------------------------------------------
                # PRODUCT MINIMUM QUANTITY
                # ---------------------------------------------

                if (
                    cart_item.quantity
                    <
                    product.min_order_qty
                ):

                    raise HTTPException(
                        status_code=(
                            status.HTTP_400_BAD_REQUEST
                        ),
                        detail=(
                            f"Minimum order quantity "
                            f"for {product.name} is "
                            f"{product.min_order_qty}"
                        ),
                    )

                # ---------------------------------------------
                # PRODUCT MAXIMUM QUANTITY
                # ---------------------------------------------

                if (
                    product.max_order_qty
                    is not None
                    and
                    cart_item.quantity
                    >
                    product.max_order_qty
                ):

                    raise HTTPException(
                        status_code=(
                            status.HTTP_400_BAD_REQUEST
                        ),
                        detail=(
                            f"Maximum order quantity "
                            f"for {product.name} is "
                            f"{product.max_order_qty}"
                        ),
                    )

                # ---------------------------------------------
                # CURRENT PRODUCT PRICE
                #
                # Never trust price stored in Flutter cart.
                # ---------------------------------------------

                effective_price = (
                    product.discount_price
                    if
                    product.discount_price
                    is not None
                    else
                    product.price
                )

                line_total = (
                    effective_price
                    *
                    cart_item.quantity
                )

                subtotal += (
                    line_total
                )

                validated_items.append(
                    (
                        cart_item,
                        product,
                        inventory,
                        effective_price,
                        line_total,
                    )
                )

            # =================================================
            # 4. COMMERCE PRICING
            #
            # Fetches CURRENT:
            #
            # - minimum order amount
            # - delivery fee
            #
            # Also rejects order when subtotal is below the
            # configured minimum.
            #
            # This happens BEFORE any inventory quantity is
            # modified.
            # =================================================

            pricing = (
                await self.pricing_service
                .calculate(
                    subtotal=subtotal,

                    # No coupon system yet.
                    discount=Decimal(
                        "0.00"
                    ),
                )
            )

            subtotal = (
                pricing[
                    "subtotal"
                ]
            )

            delivery_fee = (
                pricing[
                    "delivery_fee"
                ]
            )

            discount_amount = (
                pricing[
                    "discount"
                ]
            )

            total_amount = (
                pricing[
                    "total"
                ]
            )

            # =================================================
            # 5. CREATE ORDER
            # =================================================

            order = Order(

                order_number=(
                    generate_order_number()
                ),

                user_id=(
                    user_id
                ),

                source_address_id=(
                    address.id
                ),

                order_status=(
                    "PLACED"
                ),

                payment_status=(
                    "PENDING"
                ),

                # ---------------------------------------------
                # PRICE SNAPSHOT
                #
                # These values are stored permanently on the
                # order.
                #
                # Future commerce-setting changes will NOT
                # modify this order.
                # ---------------------------------------------

                subtotal=(
                    subtotal
                ),

                delivery_fee=(
                    delivery_fee
                ),

                discount_amount=(
                    discount_amount
                ),

                total_amount=(
                    total_amount
                ),

                customer_note=(
                    customer_note
                ),

                # ---------------------------------------------
                # DELIVERY ADDRESS SNAPSHOT
                # ---------------------------------------------

                delivery_full_name=(
                    address.full_name
                ),

                delivery_phone=(
                    address.phone
                ),

                delivery_house_no=(
                    address.house_no
                ),

                delivery_street=(
                    address.street
                ),

                delivery_village_town=(
                    address.village_town
                ),

                delivery_mandal=(
                    address.mandal
                ),

                delivery_district=(
                    address.district
                ),

                delivery_state=(
                    address.state
                ),

                delivery_pincode=(
                    address.pincode
                ),

                delivery_landmark=(
                    address.landmark
                ),

                delivery_latitude=(
                    address.latitude
                ),

                delivery_longitude=(
                    address.longitude
                ),
            )

            self.db.add(
                order
            )

            # Need order.id for:
            # - order items
            # - inventory transaction
            # - payment
            # - status history
            # - notification

            await self.db.flush()

            # =================================================
            # 6. CREATE ORDER ITEMS + RESERVE STOCK
            # =================================================

            for (
                cart_item,
                product,
                inventory,
                effective_price,
                line_total,
            ) in validated_items:

                original_price_total = (
                    product.price
                    *
                    cart_item.quantity
                )

                item_discount = (
                    original_price_total
                    -
                    line_total
                )

                order_item = (
                    OrderItem(

                        order_id=(
                            order.id
                        ),

                        product_id=(
                            product.id
                        ),

                        product_name=(
                            product.name
                        ),

                        product_sku=(
                            product.sku
                        ),

                        unit=(
                            product.unit
                        ),

                        unit_value=(
                            product.unit_value
                        ),

                        quantity=(
                            cart_item.quantity
                        ),

                        unit_price=(
                            effective_price
                        ),

                        discount_amount=(
                            item_discount
                        ),

                        line_total=(
                            line_total
                        ),
                    )
                )

                self.db.add(
                    order_item
                )

                # ---------------------------------------------
                # RESERVE STOCK
                # ---------------------------------------------

                inventory.reserved_quantity += (
                    cart_item.quantity
                )

                # ---------------------------------------------
                # INVENTORY LEDGER
                # ---------------------------------------------

                inventory_transaction = (
                    InventoryTransaction(

                        product_id=(
                            product.id
                        ),

                        transaction_type=(
                            "ORDER_RESERVED"
                        ),

                        quantity=(
                            cart_item.quantity
                        ),

                        reference_type=(
                            "ORDER"
                        ),

                        reference_id=(
                            order.id
                        ),

                        note=(
                            f"Reserved for "
                            f"{order.order_number}"
                        ),

                        created_by=(
                            user_id
                        ),
                    )
                )

                self.db.add(
                    inventory_transaction
                )

            # =================================================
            # 7. COD PAYMENT
            # =================================================

            payment = Payment(

                order_id=(
                    order.id
                ),

                method=(
                    "COD"
                ),

                status=(
                    "PENDING"
                ),

                amount=(
                    total_amount
                ),

                provider=(
                    None
                ),

                transaction_id=(
                    None
                ),
            )

            self.db.add(
                payment
            )

            # =================================================
            # 8. INITIAL ORDER STATUS HISTORY
            # =================================================

            status_history = (
                OrderStatusHistory(

                    order_id=(
                        order.id
                    ),

                    from_status=(
                        None
                    ),

                    to_status=(
                        "PLACED"
                    ),

                    changed_by=(
                        user_id
                    ),

                    note=(
                        "Order placed by customer"
                    ),
                )
            )

            self.db.add(
                status_history
            )

            # =================================================
            # 9. CONVERT ACTIVE CART
            # =================================================

            cart.status = (
                "CONVERTED"
            )

            # =================================================
            # 10. CREATE ORDER PLACED NOTIFICATION
            #
            # Keep notification creation in same transaction.
            # =================================================

            await self.notification_service.create(

                user_id=(
                    user_id
                ),

                notification_type=(
                    "ORDER_PLACED"
                ),

                title=(
                    "Order Placed ✅"
                ),

                message=(
                    f"Your order "
                    f"{order.order_number} "
                    f"has been placed successfully."
                ),

                action=(
                    "OPEN_ORDER"
                ),

                reference_type=(
                    "ORDER"
                ),

                reference_id=(
                    order.id
                ),
            )

            # =================================================
            # 11. COMMIT EVERYTHING
            #
            # Order
            # Items
            # Inventory reservations
            # Inventory ledger
            # Payment
            # Status history
            # Notification
            # Converted cart
            #
            # Either all commit or all rollback.
            # =================================================

            await self.db.commit()

            # =================================================
            # 12. REFRESH ORDER
            # =================================================

            await self.db.refresh(
                order
            )

            return order

        # =====================================================
        # KNOWN BUSINESS/API ERROR
        # =====================================================

        except HTTPException:

            await self.db.rollback()

            raise

        # =====================================================
        # UNKNOWN SERVER ERROR
        # =====================================================

        except Exception as exc:

            await self.db.rollback()

            logger.exception(
                "Checkout failed"
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Unable to place order"
                ),
            ) from exc