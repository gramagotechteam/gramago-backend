from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy.orm import (
    selectinload,
)

from app.models.order import Order
from app.models.delivery_assignment import (
    DeliveryAssignment,
)
from app.models.user import User


class DeliveryOrderService:

    # ============================================================
    # ASSIGNED ORDERS
    # ============================================================

    @staticmethod
    async def get_assigned_orders(
        db: AsyncSession,
        partner: User,
    ) -> list[DeliveryAssignment]:

        result = await db.execute(
            select(
                DeliveryAssignment
            )
            .options(
                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.items
                ),

                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.payment
                ),
            )
            .where(
                DeliveryAssignment
                .delivery_partner_id
                == partner.id,

                DeliveryAssignment.status.in_(
                    [
                        "ASSIGNED",
                        "ACCEPTED",
                        "PICKED_UP",
                        "OUT_FOR_DELIVERY",
                    ]
                ),
            )
            .order_by(
                DeliveryAssignment
                .assigned_at
                .desc()
            )
        )

        return list(
            result.scalars().all()
        )


    # ============================================================
    # ONE ASSIGNED ORDER
    # ============================================================

    @staticmethod
    async def get_order(
        db: AsyncSession,
        partner: User,
        order_id: int,
    ) -> DeliveryAssignment:

        result = await db.execute(
            select(
                DeliveryAssignment
            )
            .options(
                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.items
                ),

                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.payment
                ),
            )
            .where(
                DeliveryAssignment.order_id
                == order_id,

                DeliveryAssignment
                .delivery_partner_id
                == partner.id,
            )
            .order_by(
                DeliveryAssignment
                .assigned_at
                .desc()
            )
        )

        assignment = (
            result.scalars().first()
        )

        if assignment is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "Assigned delivery order not found"
                ),
            )

        return assignment
    
    
    
    
        

    @staticmethod
    async def get_active_delivery(
        db: AsyncSession,
        partner: User,
    ) -> DeliveryAssignment | None:

        active_statuses = [
            "ASSIGNED",
            "ACCEPTED",
            "PICKED_UP",
            "OUT_FOR_DELIVERY",
        ]

        result = await db.execute(
            select(
                DeliveryAssignment
            )
            .options(
                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.items
                ),

                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.payment
                ),
            )
            .where(
                DeliveryAssignment
                .delivery_partner_id
                == partner.id,

                DeliveryAssignment
                .status
                .in_(
                    active_statuses
                ),
            )
            .order_by(
                DeliveryAssignment
                .assigned_at
                .desc()
            )
            .limit(1)
        )

        return (
            result.scalar_one_or_none()
        )





    @staticmethod
    async def get_history(
        db: AsyncSession,
        partner: User,
    ) -> list[DeliveryAssignment]:

        history_statuses = [
            "DELIVERED",
            "REJECTED",
            "FAILED",
            "CANCELLED",
        ]

        result = await db.execute(
            select(
                DeliveryAssignment
            )
            .options(
                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.items
                ),

                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.payment
                ),
            )
            .where(
                DeliveryAssignment
                .delivery_partner_id
                == partner.id,

                DeliveryAssignment
                .status
                .in_(
                    history_statuses
                ),
            )
            .order_by(
                DeliveryAssignment
                .updated_at
                .desc()
            )
        )

        return list(
            result.scalars().all()
        )
        
        
    

def delivery_order_response(
        assignment: DeliveryAssignment,
    ) -> dict:

        order = assignment.order

        payment = order.payment

        return {
            "assignment": {
                "id": assignment.id,

                "status": (
                    assignment.status
                ),

                "assigned_at": (
                    assignment.assigned_at
                ),

                "delivery_note": (
                    assignment.delivery_note
                ),
            },

            "order": {
                "id": order.id,

                "order_number": (
                    order.order_number
                ),

                "order_status": (
                    order.order_status
                ),

                "payment_status": (
                    order.payment_status
                ),

                "subtotal": (
                    float(order.subtotal)
                ),

                "delivery_fee": (
                    float(order.delivery_fee)
                ),

                "discount_amount": (
                    float(
                        order.discount_amount
                    )
                ),

                "total_amount": (
                    float(order.total_amount)
                ),

                "customer_note": (
                    order.customer_note
                ),

                "placed_at": (
                    order.placed_at
                ),
            },

            "customer": {
                "full_name": (
                    order.delivery_full_name
                ),

                "phone": (
                    order.delivery_phone
                ),
            },

            "delivery_address": {
                "house_no": (
                    order.delivery_house_no
                ),

                "street": (
                    order.delivery_street
                ),

                "village_town": (
                    order.delivery_village_town
                ),

                "mandal": (
                    order.delivery_mandal
                ),

                "district": (
                    order.delivery_district
                ),

                "state": (
                    order.delivery_state
                ),

                "pincode": (
                    order.delivery_pincode
                ),

                "landmark": (
                    order.delivery_landmark
                ),

                "latitude": (
                    float(
                        order.delivery_latitude
                    )
                    if order.delivery_latitude
                    is not None
                    else None
                ),

                "longitude": (
                    float(
                        order.delivery_longitude
                    )
                    if order.delivery_longitude
                    is not None
                    else None
                ),
            },

            "payment": {
                "method": (
                    payment.method
                    if payment
                    else None
                ),

                "status": (
                    payment.status
                    if payment
                    else order.payment_status
                ),

                "amount": (
                    float(payment.amount)
                    if payment
                    else float(
                        order.total_amount
                    )
                ),
            },

            "items": [
                {
                    "id": item.id,

                    "product_id": (
                        item.product_id
                    ),

                    "product_name": (
                        item.product_name
                    ),

                    "unit": item.unit,

                    "unit_value": (
                        float(
                            item.unit_value
                        )
                    ),

                    "quantity": (
                        float(
                            item.quantity
                        )
                    ),

                    "unit_price": (
                        float(
                            item.unit_price
                        )
                    ),

                    "line_total": (
                        float(
                            item.line_total
                        )
                    ),
                }

                for item in order.items
            ],
        }