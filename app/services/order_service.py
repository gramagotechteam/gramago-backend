from datetime import datetime, timezone

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

class OrderService:

    CUSTOMER_CANCEL_STATES = {
        "PLACED",
        "CONFIRMED",
    }

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db
        
        self.notification_service = (
    NotificationService(db)
)


    async def cancel_customer_order(
        self,
        order_id: int,
        user_id: int,
    ) -> None:

        try:

            # ---------------------------------
            # 1. Lock order
            # ---------------------------------

            result = await self.db.execute(
                select(Order)
                .where(
                    Order.id == order_id,
                    Order.user_id == user_id,
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
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found",
                )


            # ---------------------------------
            # 2. Validate cancellation state
            # ---------------------------------

            if (
                order.order_status
                not in self.CUSTOMER_CANCEL_STATES
            ):

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "This order can no longer "
                        "be cancelled"
                    ),
                )


            previous_status = (
                order.order_status
            )


            # ---------------------------------
            # 3. Release reserved inventory
            # ---------------------------------

            for item in order.items:

                # Product could theoretically
                # become NULL later if deleted.
                if item.product_id is None:
                    continue

                inventory_result = (
                    await self.db.execute(
                        select(Inventory)
                        .where(
                            Inventory.product_id
                            == item.product_id
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
                            status.HTTP_409_CONFLICT
                        ),
                        detail=(
                            "Inventory record missing "
                            f"for product {item.product_name}"
                        ),
                    )


                # ---------------------------------
                # Safety validation
                # ---------------------------------

                if (
                    inventory.reserved_quantity
                    < item.quantity
                ):

                    raise HTTPException(
                        status_code=(
                            status.HTTP_409_CONFLICT
                        ),
                        detail=(
                            "Reserved inventory is "
                            "inconsistent for "
                            f"{item.product_name}"
                        ),
                    )


                inventory.reserved_quantity -= (
                    item.quantity
                )


                # ---------------------------------
                # Inventory history
                # ---------------------------------

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

                        reference_type=(
                            "ORDER"
                        ),

                        reference_id=(
                            order.id
                        ),

                        note=(
                            "Reservation released "
                            f"for cancelled order "
                            f"{order.order_number}"
                        ),

                        created_by=(
                            user_id
                        ),
                    )
                )

                self.db.add(
                    transaction
                )


            # ---------------------------------
            # 4. Update order status
            # ---------------------------------

            now = datetime.now(
                timezone.utc
            )

            order.order_status = (
                "CANCELLED"
            )

            order.cancelled_at = now


            # ---------------------------------
            # 5. Cancel COD payment
            # ---------------------------------

            if order.payment:

                order.payment.status = (
                    "CANCELLED"
                )

                order.payment_status = (
                    "CANCELLED"
                )


            # ---------------------------------
            # 6. Add status history
            # ---------------------------------

            history = OrderStatusHistory(
                order_id=order.id,

                from_status=(
                    previous_status
                ),

                to_status="CANCELLED",

                changed_by=user_id,

                note=(
                    "Cancelled by customer"
                ),
            )

            self.db.add(
                history
            )


            # ---------------------------------
            # 7. Commit all changes
            # ---------------------------------
            
            
            await self.notification_service.create(
    user_id=user_id,
    notification_type="ORDER_CANCELLED",
    title="Order cancelled",
    message=(
        f"Your order "
        f"{order.order_number} "
        f"was cancelled."
    ),
    reference_type="ORDER",
    reference_id=order.id,
)

            await self.db.commit()


        except HTTPException:

            await self.db.rollback()

            raise


        except Exception:

            await self.db.rollback()

            raise