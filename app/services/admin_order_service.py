


# from datetime import datetime, timezone

# from fastapi import (
#     HTTPException,
#     status,
# )
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload

# from app.core.order_status import (
#     ORDER_TRANSITIONS,
# )
# from app.models.inventory import Inventory
# from app.models.inventory_transaction import (
#     InventoryTransaction,
# )
# from app.models.order import Order
# from app.models.order_status_history import (
#     OrderStatusHistory,
# )

# from app.services.notification_service import (
#     NotificationService,
# )
# from app.services.audit_service import (
#     AuditService,
# )


# class AdminOrderService:
#     ORDER_NOTIFICATION_CONFIG = {

#     "CONFIRMED": {
#         "type": "ORDER_CONFIRMED",
#         "title": "Order Confirmed ✅",
#         "message": (
#             "Your order has been confirmed."
#         ),
#     },

#     "PROCESSING": {
#         "type": "ORDER_PROCESSING",
#         "title": "Order Processing",
#         "message": (
#             "Your order is being prepared."
#         ),
#     },

#     "PACKED": {
#         "type": "ORDER_PACKED",
#         "title": "Order Packed 📦",
#         "message": (
#             "Your order has been packed "
#             "and is getting ready for delivery."
#         ),
#     },

#     "OUT_FOR_DELIVERY": {
#         "type": "ORDER_OUT_FOR_DELIVERY",
#         "title": "Out for Delivery 🚚",
#         "message": (
#             "Your order is on the way."
#         ),
#     },

#     "DELIVERED": {
#         "type": "ORDER_DELIVERED",
#         "title": "Order Delivered ✅",
#         "message": (
#             "Your order has been delivered "
#             "successfully."
#         ),
#     },

#     "CANCELLED": {
#         "type": "ORDER_CANCELLED",
#         "title": "Order Cancelled",
#         "message": (
#             "Your order has been cancelled."
#         ),
#     },

#     "DELIVERY_FAILED": {
#         "type": "ORDER_DELIVERY_FAILED",
#         "title": "Delivery Unsuccessful",
#         "message": (
#             "We could not complete the delivery."
#         ),
#     },
# }

#     # ==================================================
#     # Constructor
#     # ==================================================

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db

#         self.notification_service = (
#             NotificationService(db)
#         )

#         self.audit_service = (
#             AuditService(db)
#         )


#     # ==================================================
#     # Update Order Status
#     # ==================================================

#     async def update_status(
#         self,
#         order_id: int,
#         new_status: str,
#         admin_id: int,
#         note: str | None = None,
#     ) -> Order:

#         try:

#             # ------------------------------------------
#             # 1. Lock order
#             # ------------------------------------------

#             result = await self.db.execute(
#                 select(Order)
#                 .where(
#                     Order.id == order_id
#                 )
#                 .options(
#                     selectinload(
#                         Order.items
#                     ),
#                     selectinload(
#                         Order.payment
#                     ),
#                 )
#                 .with_for_update()
#             )

#             order = (
#                 result.scalar_one_or_none()
#             )

#             if not order:

#                 raise HTTPException(
#                     status_code=(
#                         status.HTTP_404_NOT_FOUND
#                     ),
#                     detail="Order not found",
#                 )


#             current_status = (
#                 order.order_status
#             )


#             # ------------------------------------------
#             # 2. Validate transition
#             # ------------------------------------------

#             allowed = (
#                 ORDER_TRANSITIONS.get(
#                     current_status,
#                     set(),
#                 )
#             )

#             if new_status not in allowed:

#                 raise HTTPException(
#                     status_code=(
#                         status.HTTP_400_BAD_REQUEST
#                     ),
#                     detail=(
#                         f"Cannot change order from "
#                         f"{current_status} "
#                         f"to {new_status}"
#                     ),
#                 )


#             now = datetime.now(
#                 timezone.utc
#             )


#             # ------------------------------------------
#             # 3. Handle DELIVERED
#             # ------------------------------------------

#             if new_status == "DELIVERED":

#                 await self._complete_delivery(
#                     order=order,
#                     admin_id=admin_id,
#                 )

#                 order.delivered_at = now


#             # ------------------------------------------
#             # 4. Handle CANCELLED
#             # ------------------------------------------

#             elif new_status == "CANCELLED":

#                 await self._cancel_order(
#                     order=order,
#                     admin_id=admin_id,
#                 )

#                 order.cancelled_at = now


#             # ------------------------------------------
#             # 5. Handle DELIVERY_FAILED
#             # ------------------------------------------

#             elif (
#                 new_status
#                 == "DELIVERY_FAILED"
#             ):

#                 await self._delivery_failed(
#                     order=order,
#                     admin_id=admin_id,
#                 )


#             # ------------------------------------------
#             # 6. Normal status timestamps
#             # ------------------------------------------

#             elif new_status == "CONFIRMED":

#                 order.confirmed_at = now


#             elif new_status == "PROCESSING":

#                 order.processing_at = now


#             elif new_status == "PACKED":

#                 order.packed_at = now


#             elif (
#                 new_status
#                 == "OUT_FOR_DELIVERY"
#             ):

#                 order.out_for_delivery_at = (
#                     now
#                 )


#             # ------------------------------------------
#             # 7. Update order status
#             # ------------------------------------------

#             order.order_status = (
#                 new_status
#             )


#             # ------------------------------------------
#             # 8. Order Status History
#             # ------------------------------------------

#             history = (
#                 OrderStatusHistory(
#                     order_id=order.id,

#                     from_status=(
#                         current_status
#                     ),

#                     to_status=(
#                         new_status
#                     ),

#                     changed_by=(
#                         admin_id
#                     ),

#                     note=note,
#                 )
#             )

#             self.db.add(
#                 history
#             )
                   
#             notification = None

#             notification_config = (
#                 self.ORDER_NOTIFICATION_CONFIG.get(
#                     new_status
#                 )
#             )


#             if notification_config:

#                 notification = (
#                     await self.notification_service.create(

#                         user_id=order.user_id,

#                         notification_type=(
#                             notification_config[
#                                 "type"
#                             ]
#                         ),

#                         category="ORDERS",

#                         title=(
#                             notification_config[
#                                 "title"
#                             ]
#                         ),

#                         message=(
#                             f"{notification_config['message']} "
#                             f"Order: {order.order_number}"
#                         ),

#                         action="OPEN_ORDER",

#                         reference_type="ORDER",

#                         reference_id=order.id,
#                     )
#                 )


#             # ------------------------------------------
#             # 10. Admin Audit Log
#             # ------------------------------------------

#             await self.audit_service.log(

#                 admin_user_id=(
#                     admin_id
#                 ),

#                 action=(
#                     "ORDER_STATUS_UPDATE"
#                 ),

#                 entity_type="ORDER",

#                 entity_id=(
#                     order.id
#                 ),

#                 description=(
#                     f"Order status changed "
#                     f"from {current_status} "
#                     f"to {new_status}"
#                 ),

#                 old_data={
#                     "order_status":
#                         current_status,
#                 },

#                 new_data={
#                     "order_status":
#                         new_status,
#                 },
#             )
            
            
            
#             # ---------------------------------
#             # 11. Commit database transaction
#             # ---------------------------------

#             await self.db.commit()


#             await self.db.refresh(
#                 order
#             )


#             if notification is not None:

#                 await self.db.refresh(
#                     notification
#                 )


#             # ---------------------------------
#             # 12. Send FCM after commit
#             # ---------------------------------

#             if notification is not None:

#                 await self._send_order_push(
#                     order=order,
#                     notification=notification,
#                 )



#             return order
        
    
#     async def _send_order_push(
#     self,
#     *,
#     order: Order,
#     notification,
#     ):
        
#         try:

#             # We will put your EXISTING
#             # working personal push sender here.

#             pass

#         except Exception:

#             logger.exception(
#                 (
#                     "Failed to send order "
#                     "push notification. "
#                     "order_id=%s "
#                     "user_id=%s"
#                 ),
#                 order.id,
#                 order.user_id,
#             )


#         except HTTPException:

#             await self.db.rollback()

#             raise


#         except Exception:

#             await self.db.rollback()

#             raise


#     # ==================================================
#     # Complete Delivery
#     # ==================================================

#     async def _complete_delivery(
#         self,
#         order: Order,
#         admin_id: int,
#     ):

#         for item in order.items:

#             if item.product_id is None:

#                 raise HTTPException(
#                     status_code=409,
#                     detail=(
#                         "Cannot complete delivery "
#                         "because product reference "
#                         f"is missing for "
#                         f"{item.product_name}"
#                     ),
#                 )


#             result = await self.db.execute(
#                 select(Inventory)
#                 .where(
#                     Inventory.product_id
#                     == item.product_id
#                 )
#                 .with_for_update()
#             )


#             inventory = (
#                 result.scalar_one_or_none()
#             )


#             if not inventory:

#                 raise HTTPException(
#                     status_code=409,
#                     detail=(
#                         "Inventory not found for "
#                         f"{item.product_name}"
#                     ),
#                 )


#             # ------------------------------------------
#             # Validate reserved stock
#             # ------------------------------------------

#             if (
#                 inventory.reserved_quantity
#                 < item.quantity
#             ):

#                 raise HTTPException(
#                     status_code=409,
#                     detail=(
#                         "Reserved stock is inconsistent "
#                         f"for {item.product_name}"
#                     ),
#                 )


#             # ------------------------------------------
#             # Validate available stock
#             # ------------------------------------------

#             if (
#                 inventory.available_quantity
#                 < item.quantity
#             ):

#                 raise HTTPException(
#                     status_code=409,
#                     detail=(
#                         "Available stock is inconsistent "
#                         f"for {item.product_name}"
#                     ),
#                 )


#             # ------------------------------------------
#             # Deduct physical stock
#             # ------------------------------------------

#             inventory.available_quantity -= (
#                 item.quantity
#             )


#             # ------------------------------------------
#             # Release reservation
#             # ------------------------------------------

#             inventory.reserved_quantity -= (
#                 item.quantity
#             )


#             # ------------------------------------------
#             # Inventory ledger
#             # ------------------------------------------

#             transaction = (
#                 InventoryTransaction(

#                     product_id=(
#                         item.product_id
#                     ),

#                     transaction_type=(
#                         "ORDER_SOLD"
#                     ),

#                     quantity=(
#                         item.quantity
#                     ),

#                     reference_type="ORDER",

#                     reference_id=(
#                         order.id
#                     ),

#                     note=(
#                         "Stock sold for delivered "
#                         f"order "
#                         f"{order.order_number}"
#                     ),

#                     created_by=(
#                         admin_id
#                     ),
#                 )
#             )


#             self.db.add(
#                 transaction
#             )


#         # ----------------------------------------------
#         # COD Payment becomes PAID
#         # ----------------------------------------------

#         if order.payment:

#             order.payment.status = (
#                 "PAID"
#             )

#             order.payment.paid_at = (
#                 datetime.now(
#                     timezone.utc
#                 )
#             )


#         order.payment_status = (
#             "PAID"
#         )


#     # ==================================================
#     # Cancel Order
#     # ==================================================

#     async def _cancel_order(
#         self,
#         order: Order,
#         admin_id: int,
#     ):

#         for item in order.items:

#             if item.product_id is None:
#                 continue


#             result = await self.db.execute(
#                 select(Inventory)
#                 .where(
#                     Inventory.product_id
#                     == item.product_id
#                 )
#                 .with_for_update()
#             )


#             inventory = (
#                 result.scalar_one_or_none()
#             )


#             if not inventory:

#                 raise HTTPException(
#                     status_code=409,
#                     detail=(
#                         "Inventory not found for "
#                         f"{item.product_name}"
#                     ),
#                 )


#             if (
#                 inventory.reserved_quantity
#                 < item.quantity
#             ):

#                 raise HTTPException(
#                     status_code=409,
#                     detail=(
#                         "Reserved inventory is "
#                         "inconsistent for "
#                         f"{item.product_name}"
#                     ),
#                 )


#             # ------------------------------------------
#             # Release reservation
#             # ------------------------------------------

#             inventory.reserved_quantity -= (
#                 item.quantity
#             )


#             # ------------------------------------------
#             # Inventory ledger
#             # ------------------------------------------

#             transaction = (
#                 InventoryTransaction(

#                     product_id=(
#                         item.product_id
#                     ),

#                     transaction_type=(
#                         "ORDER_CANCELLED"
#                     ),

#                     quantity=(
#                         item.quantity
#                     ),

#                     reference_type="ORDER",

#                     reference_id=(
#                         order.id
#                     ),

#                     note=(
#                         "Reservation released "
#                         "for cancelled order "
#                         f"{order.order_number}"
#                     ),

#                     created_by=(
#                         admin_id
#                     ),
#                 )
#             )


#             self.db.add(
#                 transaction
#             )


#         # ----------------------------------------------
#         # Cancel COD Payment
#         # ----------------------------------------------

#         if order.payment:

#             order.payment.status = (
#                 "CANCELLED"
#             )


#         order.payment_status = (
#             "CANCELLED"
#         )


#     # ==================================================
#     # Delivery Failed
#     # ==================================================

#     async def _delivery_failed(
#         self,
#         order: Order,
#         admin_id: int,
#     ):

#         for item in order.items:

#             if item.product_id is None:
#                 continue


#             result = await self.db.execute(
#                 select(Inventory)
#                 .where(
#                     Inventory.product_id
#                     == item.product_id
#                 )
#                 .with_for_update()
#             )


#             inventory = (
#                 result.scalar_one_or_none()
#             )


#             if not inventory:

#                 raise HTTPException(
#                     status_code=409,
#                     detail=(
#                         "Inventory not found for "
#                         f"{item.product_name}"
#                     ),
#                 )


#             if (
#                 inventory.reserved_quantity
#                 < item.quantity
#             ):

#                 raise HTTPException(
#                     status_code=409,
#                     detail=(
#                         "Reserved inventory "
#                         "is inconsistent for "
#                         f"{item.product_name}"
#                     ),
#                 )


#             # ------------------------------------------
#             # Release reservation
#             # ------------------------------------------

#             inventory.reserved_quantity -= (
#                 item.quantity
#             )


#             # ------------------------------------------
#             # Inventory ledger
#             # ------------------------------------------

#             transaction = (
#                 InventoryTransaction(

#                     product_id=(
#                         item.product_id
#                     ),

#                     transaction_type=(
#                         "ORDER_CANCELLED"
#                     ),

#                     quantity=(
#                         item.quantity
#                     ),

#                     reference_type="ORDER",

#                     reference_id=(
#                         order.id
#                     ),

#                     note=(
#                         "Reservation released "
#                         "after delivery failure "
#                         f"for "
#                         f"{order.order_number}"
#                     ),

#                     created_by=(
#                         admin_id
#                     ),
#                 )
#             )


#             self.db.add(
#                 transaction
#             )


#         # ----------------------------------------------
#         # Payment failed
#         # ----------------------------------------------

#         if order.payment:

#             order.payment.status = (
#                 "FAILED"
#             )


#         order.payment_status = (
#             "FAILED"
#         )






















# import logging

# from datetime import datetime, timezone

# from fastapi import (
#     HTTPException,
#     status,
# )
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload

# from app.core.order_status import (
#     ORDER_TRANSITIONS,
# )
# from app.models.inventory import Inventory
# from app.models.inventory_transaction import (
#     InventoryTransaction,
# )
# from app.models.order import Order
# from app.models.order_status_history import (
#     OrderStatusHistory,
# )

# from app.services.notification_service import (
#     NotificationService,
# )
# from app.services.audit_service import (
#     AuditService,
# )


# logger = logging.getLogger(__name__)




import logging

from datetime import datetime, timezone

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.order_status import (
    ORDER_TRANSITIONS,
)

from app.models.inventory import Inventory

from app.models.inventory_transaction import (
    InventoryTransaction,
)

from app.models.order import Order

from app.models.order_status_history import (
    OrderStatusHistory,
)

from app.services.notification_service import (
    NotificationService,
)

from app.services.audit_service import (
    AuditService,
)


logger = logging.getLogger(__name__)

class AdminOrderService:

    ORDER_NOTIFICATION_CONFIG = {

        "CONFIRMED": {
            "type": "ORDER_CONFIRMED",
            "title": "Order Confirmed ✅",
            "message": (
                "Your order has been confirmed."
            ),
        },

        "PROCESSING": {
            "type": "ORDER_PROCESSING",
            "title": "Order Processing",
            "message": (
                "Your order is being prepared."
            ),
        },

        "PACKED": {
            "type": "ORDER_PACKED",
            "title": "Order Packed 📦",
            "message": (
                "Your order has been packed "
                "and is getting ready for delivery."
            ),
        },

        "OUT_FOR_DELIVERY": {
            "type": "ORDER_OUT_FOR_DELIVERY",
            "title": "Out for Delivery 🚚",
            "message": (
                "Your order is on the way."
            ),
        },

        "DELIVERED": {
            "type": "ORDER_DELIVERED",
            "title": "Order Delivered ✅",
            "message": (
                "Your order has been delivered "
                "successfully."
            ),
        },

        "CANCELLED": {
            "type": "ORDER_CANCELLED",
            "title": "Order Cancelled",
            "message": (
                "Your order has been cancelled."
            ),
        },

        "DELIVERY_FAILED": {
            "type": "ORDER_DELIVERY_FAILED",
            "title": "Delivery Unsuccessful",
            "message": (
                "We could not complete the delivery."
            ),
        },
    }
    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.notification_service = (
            NotificationService(db)
        )

        self.audit_service = (
            AuditService(db)
        )


    # ==================================================
    # Update Order Status
    # ==================================================

    async def update_status(
        self,
        order_id: int,
        new_status: str,
        admin_id: int,
        note: str | None = None,
    ) -> Order:

        try:

            # ------------------------------------------
            # 1. Lock order
            # ------------------------------------------

            result = await self.db.execute(
                select(Order)
                .where(
                    Order.id == order_id
                )
                .options(
                    selectinload(
                        Order.items
                    ),
                    selectinload(
                        Order.payment
                    ),
                )
                .with_for_update()
            )

            order = (
                result.scalar_one_or_none()
            )


            if not order:

                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail="Order not found",
                )


            current_status = (
                order.order_status
            )


            # ------------------------------------------
            # 2. Validate transition
            # ------------------------------------------

            allowed = (
                ORDER_TRANSITIONS.get(
                    current_status,
                    set(),
                )
            )


            if new_status not in allowed:

                raise HTTPException(
                    status_code=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                    detail=(
                        f"Cannot change order from "
                        f"{current_status} "
                        f"to {new_status}"
                    ),
                )


            now = datetime.now(
                timezone.utc
            )


            # ------------------------------------------
            # 3. Handle DELIVERED
            # ------------------------------------------

            if new_status == "DELIVERED":

                await self._complete_delivery(
                    order=order,
                    admin_id=admin_id,
                )

                order.delivered_at = now


            # ------------------------------------------
            # 4. Handle CANCELLED
            # ------------------------------------------

            elif new_status == "CANCELLED":

                await self._cancel_order(
                    order=order,
                    admin_id=admin_id,
                )

                order.cancelled_at = now


            # ------------------------------------------
            # 5. Handle DELIVERY_FAILED
            # ------------------------------------------

            elif (
                new_status ==
                "DELIVERY_FAILED"
            ):

                await self._delivery_failed(
                    order=order,
                    admin_id=admin_id,
                )


            # ------------------------------------------
            # 6. Normal status timestamps
            # ------------------------------------------

            elif new_status == "CONFIRMED":

                order.confirmed_at = now


            elif new_status == "PROCESSING":

                order.processing_at = now


            elif new_status == "PACKED":

                order.packed_at = now


            elif (
                new_status ==
                "OUT_FOR_DELIVERY"
            ):

                order.out_for_delivery_at = (
                    now
                )


            # ------------------------------------------
            # 7. Update order status
            # ------------------------------------------

            order.order_status = (
                new_status
            )


            # ------------------------------------------
            # 8. Order status history
            # ------------------------------------------

            history = (
                OrderStatusHistory(
                    order_id=order.id,

                    from_status=(
                        current_status
                    ),

                    to_status=(
                        new_status
                    ),

                    changed_by=(
                        admin_id
                    ),

                    note=note,
                )
            )

            self.db.add(
                history
            )


            # ------------------------------------------
            # 9. Create notification
            # ------------------------------------------

            notification = None


            notification_config = (
                self.ORDER_NOTIFICATION_CONFIG.get(
                    new_status
                )
            )


            if notification_config:

                notification = (
                    await self.notification_service.create(

                        user_id=order.user_id,

                        notification_type=(
                            notification_config[
                                "type"
                            ]
                        ),

                        category="ORDERS",

                        title=(
                            notification_config[
                                "title"
                            ]
                        ),

                        message=(
                            f"{notification_config['message']} "
                            f"Order: {order.order_number}"
                        ),

                        action="OPEN_ORDER",

                        reference_type="ORDER",

                        reference_id=order.id,
                    )
                )


            # ------------------------------------------
            # 10. Admin audit
            # ------------------------------------------

            await self.audit_service.log(

                admin_user_id=(
                    admin_id
                ),

                action=(
                    "ORDER_STATUS_UPDATE"
                ),

                entity_type="ORDER",

                entity_id=(
                    order.id
                ),

                description=(
                    f"Order status changed "
                    f"from {current_status} "
                    f"to {new_status}"
                ),

                old_data={
                    "order_status":
                        current_status,
                },

                new_data={
                    "order_status":
                        new_status,
                },
            )


            # ------------------------------------------
            # 11. Commit business transaction
            # ------------------------------------------

            await self.db.commit()


            await self.db.refresh(
                order
            )


            if notification is not None:

                await self.db.refresh(
                    notification
                )


            # ------------------------------------------
            # 12. Send FCM AFTER commit
            # ------------------------------------------

            if notification is not None:

                await self._send_order_push(
                    order=order,
                    notification=notification,
                )


            return order


        except HTTPException:

            await self.db.rollback()

            raise


        except Exception:

            await self.db.rollback()

            raise


    # ==================================================
    # Push order notification
    # ==================================================
    
    
    async def _send_order_push(
    self,
    *,
    order: Order,
    notification,
    ):
        
        """
        Send the already-created order notification
        through Firebase.

        Important:
        - Database transaction is already committed.
        - Push failure must NOT fail the order update.
        """

        try:

            push_result = (
                await self.notification_service.dispatch(
                    notification
                )
            )


            logger.info(
                (
                    "Order push processed. "
                    "order_id=%s "
                    "user_id=%s "
                    "notification_id=%s "
                    "result=%s"
                ),
                order.id,
                order.user_id,
                notification.id,
                push_result,
            )


            return push_result


        except Exception:

            logger.exception(
                (
                    "Failed to send order "
                    "push notification. "
                    "order_id=%s "
                    "user_id=%s "
                    "notification_id=%s"
                ),
                order.id,
                order.user_id,
                getattr(
                    notification,
                    "id",
                    None,
                ),
            )


            # IMPORTANT:
            #
            # Do not raise here.
            # The order-status database transaction
            # was already committed successfully.
            return None

    # async def _send_order_push(
    #     self,
    #     *,
    #     order: Order,
    #     notification,
    # ):

    #     try:

    #         # IMPORTANT:
    #         #
    #         # Replace this section with the SAME
    #         # push sender used by your working
    #         # /test-push endpoint.
    #         #
    #         # Example shape:
    #         #
    #         # await self.push_service.send_to_user(
    #         #     user_id=order.user_id,
    #         #     title=notification.title,
    #         #     body=notification.message,
    #         #     data={
    #         #         "type":
    #         #             notification.notification_type,
    #         #
    #         #         "category":
    #         #             "ORDERS",
    #         #
    #         #         "action":
    #         #             "OPEN_ORDER",
    #         #
    #         #         "reference_type":
    #         #             "ORDER",
    #         #
    #         #         "reference_id":
    #         #             str(order.id),
    #         #     },
    #         # )

    #         pass


    #     except Exception:

    #         # FCM failure must NOT undo the order update.
    #         logger.exception(
    #             (
    #                 "Failed to send order "
    #                 "push notification. "
    #                 "order_id=%s "
    #                 "user_id=%s"
    #             ),
    #             order.id,
    #             order.user_id,
    #         )




    # ==================================================
    # Complete Delivery
    # ==================================================

    async def _complete_delivery(
        self,
        order: Order,
        admin_id: int,
    ):

        for item in order.items:

            if item.product_id is None:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Cannot complete delivery "
                        "because product reference "
                        f"is missing for "
                        f"{item.product_name}"
                    ),
                )


            result = await self.db.execute(
                select(Inventory)
                .where(
                    Inventory.product_id
                    == item.product_id
                )
                .with_for_update()
            )


            inventory = (
                result.scalar_one_or_none()
            )


            if not inventory:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Inventory not found for "
                        f"{item.product_name}"
                    ),
                )


            # ------------------------------------------
            # Validate reserved stock
            # ------------------------------------------

            if (
                inventory.reserved_quantity
                < item.quantity
            ):

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Reserved stock is inconsistent "
                        f"for {item.product_name}"
                    ),
                )


            # ------------------------------------------
            # Validate available stock
            # ------------------------------------------

            if (
                inventory.available_quantity
                < item.quantity
            ):

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Available stock is inconsistent "
                        f"for {item.product_name}"
                    ),
                )


            # ------------------------------------------
            # Deduct physical stock
            # ------------------------------------------

            inventory.available_quantity -= (
                item.quantity
            )


            # ------------------------------------------
            # Release reservation
            # ------------------------------------------

            inventory.reserved_quantity -= (
                item.quantity
            )


            # ------------------------------------------
            # Inventory ledger
            # ------------------------------------------

            transaction = (
                InventoryTransaction(

                    product_id=(
                        item.product_id
                    ),

                    transaction_type=(
                        "ORDER_SOLD"
                    ),

                    quantity=(
                        item.quantity
                    ),

                    reference_type="ORDER",

                    reference_id=(
                        order.id
                    ),

                    note=(
                        "Stock sold for delivered "
                        f"order "
                        f"{order.order_number}"
                    ),

                    created_by=(
                        admin_id
                    ),
                )
            )


            self.db.add(
                transaction
            )


        # ----------------------------------------------
        # COD Payment becomes PAID
        # ----------------------------------------------

        if order.payment:

            order.payment.status = (
                "PAID"
            )

            order.payment.paid_at = (
                datetime.now(
                    timezone.utc
                )
            )


        order.payment_status = (
            "PAID"
        )


    # ==================================================
    # Cancel Order
    # ==================================================

    async def _cancel_order(
        self,
        order: Order,
        admin_id: int,
    ):

        for item in order.items:

            if item.product_id is None:
                continue


            result = await self.db.execute(
                select(Inventory)
                .where(
                    Inventory.product_id
                    == item.product_id
                )
                .with_for_update()
            )


            inventory = (
                result.scalar_one_or_none()
            )


            if not inventory:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Inventory not found for "
                        f"{item.product_name}"
                    ),
                )


            if (
                inventory.reserved_quantity
                < item.quantity
            ):

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Reserved inventory is "
                        "inconsistent for "
                        f"{item.product_name}"
                    ),
                )


            # ------------------------------------------
            # Release reservation
            # ------------------------------------------

            inventory.reserved_quantity -= (
                item.quantity
            )


            # ------------------------------------------
            # Inventory ledger
            # ------------------------------------------

            transaction = (
                InventoryTransaction(

                    product_id=(
                        item.product_id
                    ),

                    transaction_type=(
                        "ORDER_CANCELLED"
                    ),

                    quantity=(
                        item.quantity
                    ),

                    reference_type="ORDER",

                    reference_id=(
                        order.id
                    ),

                    note=(
                        "Reservation released "
                        "for cancelled order "
                        f"{order.order_number}"
                    ),

                    created_by=(
                        admin_id
                    ),
                )
            )


            self.db.add(
                transaction
            )


        # ----------------------------------------------
        # Cancel COD Payment
        # ----------------------------------------------

        if order.payment:

            order.payment.status = (
                "CANCELLED"
            )


        order.payment_status = (
            "CANCELLED"
        )



    # ==================================================
    # Delivery Failed
    # ==================================================

    async def _delivery_failed(
        self,
        order: Order,
        admin_id: int,
    ):

        for item in order.items:

            if item.product_id is None:
                continue


            result = await self.db.execute(
                select(Inventory)
                .where(
                    Inventory.product_id
                    == item.product_id
                )
                .with_for_update()
            )


            inventory = (
                result.scalar_one_or_none()
            )


            if not inventory:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Inventory not found for "
                        f"{item.product_name}"
                    ),
                )


            if (
                inventory.reserved_quantity
                < item.quantity
            ):

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Reserved inventory "
                        "is inconsistent for "
                        f"{item.product_name}"
                    ),
                )


            # ------------------------------------------
            # Release reservation
            # ------------------------------------------

            inventory.reserved_quantity -= (
                item.quantity
            )


            # ------------------------------------------
            # Inventory ledger
            # ------------------------------------------

            transaction = (
                InventoryTransaction(

                    product_id=(
                        item.product_id
                    ),

                    transaction_type=(
                        "ORDER_CANCELLED"
                    ),

                    quantity=(
                        item.quantity
                    ),

                    reference_type="ORDER",

                    reference_id=(
                        order.id
                    ),

                    note=(
                        "Reservation released "
                        "after delivery failure "
                        f"for "
                        f"{order.order_number}"
                    ),

                    created_by=(
                        admin_id
                    ),
                )
            )


            self.db.add(
                transaction
            )


        # ----------------------------------------------
        # Payment failed
        # ----------------------------------------------

        if order.payment:

            order.payment.status = (
                "FAILED"
            )


        order.payment_status = (
            "FAILED"
        )


