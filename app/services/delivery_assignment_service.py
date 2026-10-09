# from datetime import datetime, timezone

# from fastapi import HTTPException, status

# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload

# from app.models.user import User
# from app.models.order import Order
# from app.models.delivery_assignment import DeliveryAssignment
# from app.models.order_status_history import OrderStatusHistory


# ACTIVE_DELIVERY_STATUSES = (
#     "ASSIGNED",
#     "ACCEPTED",
#     "PICKED_UP",
#     "OUT_FOR_DELIVERY",
# )

# def delivery_assignment_response(
#         assignment: DeliveryAssignment,
#     ) -> dict:

#         return {
#             "id": assignment.id,

#             "order_id": (
#                 assignment.order_id
#             ),

#             "delivery_partner_id": (
#                 assignment.delivery_partner_id
#             ),

#             "status": (
#                 assignment.status
#             ),

#             "assigned_at": (
#                 assignment.assigned_at
#             ),

#             "accepted_at": (
#                 assignment.accepted_at
#             ),

#             "rejected_at": (
#                 assignment.rejected_at
#             ),

#             "picked_up_at": (
#                 assignment.picked_up_at
#             ),

#             "out_for_delivery_at": (
#                 assignment
#                 .out_for_delivery_at
#             ),

#             "delivered_at": (
#                 assignment.delivered_at
#             ),

#             "delivery_note": (
#                 assignment.delivery_note
#             ),
#         }
        
        
        
# class DeliveryAssignmentService:

#     # ============================================================
#     # AVAILABLE DELIVERY PARTNERS
#     # ============================================================

#     @staticmethod
#     async def get_available_partners(
#         db: AsyncSession,
#     ) -> list[User]:

#         result = await db.execute(
#             select(User)
#             .options(
#                 selectinload(
#                     User.delivery_profile
#                 )
#             )
#             .where(
#                 User.role == "DELIVERY_PARTNER",
#                 User.is_active.is_(True),
#             )
#             .order_by(
#                 User.full_name.asc()
#             )
#         )

#         users = list(
#             result.scalars().all()
#         )

#         # Filter delivery-specific profile conditions.
#         available = []

#         for user in users:

#             profile = user.delivery_profile

#             if profile is None:
#                 continue

#             if not profile.is_approved:
#                 continue

#             if not profile.is_online:
#                 continue

#             if not profile.is_available:
#                 continue

#             available.append(user)

#         return available


#     # ============================================================
#     # GET ORDER
#     # ============================================================

#     @staticmethod
#     async def get_order(
#         db: AsyncSession,
#         order_id: int,
#     ) -> Order:

#         result = await db.execute(
#             select(Order)
#             .options(
#                 selectinload(
#                     Order.delivery_assignments
#                 )
#             )
#             .where(
#                 Order.id == order_id
#             )
#         )

#         order = (
#             result.scalar_one_or_none()
#         )

#         if order is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Order not found",
#             )

#         return order


#     # ============================================================
#     # GET DELIVERY PARTNER
#     # ============================================================

#     @staticmethod
#     async def get_delivery_partner(
#         db: AsyncSession,
#         partner_id: int,
#     ) -> User:

#         result = await db.execute(
#             select(User)
#             .options(
#                 selectinload(
#                     User.delivery_profile
#                 )
#             )
#             .where(
#                 User.id == partner_id,
#                 User.role == "DELIVERY_PARTNER",
#             )
#         )

#         partner = (
#             result.scalar_one_or_none()
#         )

#         if partner is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Delivery partner not found",
#             )

#         return partner


#     # ============================================================
#     # ASSIGN ORDER
#     # ============================================================

#     @staticmethod
#     async def assign_order(
#         db: AsyncSession,
#         order_id: int,
#         partner_id: int,
#         admin_user: User,
#         delivery_note: str | None = None,
#     ) -> DeliveryAssignment:

#         # --------------------------------------------------------
#         # LOAD ORDER
#         # --------------------------------------------------------

#         order = await (
#             DeliveryAssignmentService
#             .get_order(
#                 db,
#                 order_id,
#             )
#         )

#         # --------------------------------------------------------
#         # VALID ORDER STATUS
#         # --------------------------------------------------------

#         allowed_statuses = {
#             "PACKED",
#             "READY_FOR_PICKUP",
#         }

#         if order.order_status not in allowed_statuses:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Order must be packed or ready "
#                     "for pickup before assignment"
#                 ),
#             )

#         # --------------------------------------------------------
#         # CHECK EXISTING ACTIVE ASSIGNMENT
#         # --------------------------------------------------------

#         active_statuses = {
#             "ASSIGNED",
#             "ACCEPTED",
#             "PICKED_UP",
#             "OUT_FOR_DELIVERY",
#         }

#         for assignment in order.delivery_assignments:

#             if assignment.status in active_statuses:
#                 raise HTTPException(
#                     status_code=status.HTTP_409_CONFLICT,
#                     detail=(
#                         "Order already has an active "
#                         "delivery assignment"
#                     ),
#                 )

#         # --------------------------------------------------------
#         # LOAD PARTNER
#         # --------------------------------------------------------

#         partner = await (
#             DeliveryAssignmentService
#             .get_delivery_partner(
#                 db,
#                 partner_id,
#             )
#         )

#         profile = (
#             partner.delivery_profile
#         )

#         if profile is None:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Delivery partner profile not found"
#                 ),
#             )

#         # --------------------------------------------------------
#         # PARTNER VALIDATION
#         # --------------------------------------------------------

#         if not partner.is_active:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Delivery partner account is inactive"
#                 ),
#             )

#         if not profile.is_approved:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Delivery partner is not approved"
#                 ),
#             )

#         if not profile.is_online:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Delivery partner is offline"
#                 ),
#             )

#         if not profile.is_available:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=(
#                     "Delivery partner is currently unavailable"
#                 ),
#             )

#         # --------------------------------------------------------
#         # CREATE ASSIGNMENT
#         # --------------------------------------------------------

#         assignment = DeliveryAssignment(
#             order_id=order.id,

#             delivery_partner_id=partner.id,

#             status="ASSIGNED",

#             delivery_note=(
#                 delivery_note.strip()
#                 if delivery_note
#                 else None
#             ),
#         )

#         db.add(
#             assignment
#         )

#         # --------------------------------------------------------
#         # UPDATE ORDER
#         # --------------------------------------------------------

#         previous_status = (
#             order.order_status
#         )

#         now = datetime.now(
#             timezone.utc
#         )

#         order.order_status = "ASSIGNED"
#         order.assigned_at = now

#         # --------------------------------------------------------
#         # MARK PARTNER BUSY
#         # --------------------------------------------------------

#         profile.is_available = False

#         # --------------------------------------------------------
#         # ORDER STATUS HISTORY
#         # --------------------------------------------------------

#         history = OrderStatusHistory(
#             order_id=order.id,

#             from_status=previous_status,

#             to_status="ASSIGNED",

#             changed_by=admin_user.id,

#             note=(
#                 f"Order assigned to delivery "
#                 f"partner {partner.full_name}"
#             ),
#         )

#         db.add(
#             history
#         )

#         # --------------------------------------------------------
#         # COMMIT
#         # --------------------------------------------------------

#         try:
#             await db.commit()

#         except Exception:
#             await db.rollback()
#             raise

#         await db.refresh(
#             assignment
#         )

#         return assignment
    
    
    
    


import logging

logger = logging.getLogger(
    __name__
)

# from asyncio.log import logger
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.order import Order
from app.models.delivery_assignment import DeliveryAssignment
from app.models.order_status_history import OrderStatusHistory




from app.services.delivery_push_notification_service import (
    DeliveryPushNotificationService,
)


ACTIVE_DELIVERY_STATUSES = (
    "ASSIGNED",
    "ACCEPTED",
    "PICKED_UP",
    "OUT_FOR_DELIVERY",
)

from app.services.notification_service import (
    NotificationService,
)


def delivery_assignment_response(
    assignment: DeliveryAssignment,
) -> dict:
    return {
        "id": assignment.id,
        "order_id": assignment.order_id,
        "delivery_partner_id": assignment.delivery_partner_id,
        "status": assignment.status,
        "assigned_at": assignment.assigned_at,
        "accepted_at": assignment.accepted_at,
        "rejected_at": assignment.rejected_at,
        "picked_up_at": assignment.picked_up_at,
        "out_for_delivery_at": assignment.out_for_delivery_at,
        "delivered_at": assignment.delivered_at,
        "delivery_note": assignment.delivery_note,
    }


class DeliveryAssignmentService:

    # ============================================================
    # ACTIVE DELIVERY COUNT
    # ============================================================

    @staticmethod
    async def get_active_delivery_count(
        db: AsyncSession,
        partner_id: int,
    ) -> int:
        result = await db.execute(
            select(func.count(DeliveryAssignment.id)).where(
                DeliveryAssignment.delivery_partner_id == partner_id,
                DeliveryAssignment.status.in_(ACTIVE_DELIVERY_STATUSES),
            )
        )

        return int(result.scalar_one() or 0)

    # ============================================================
    # SYNC PARTNER AVAILABILITY
    # ============================================================

    @staticmethod
    async def sync_partner_availability(
        db: AsyncSession,
        partner: User,
    ) -> int:
        profile = partner.delivery_profile

        if profile is None:
            return 0

        active_count = await DeliveryAssignmentService.get_active_delivery_count(
            db,
            partner.id,
        )

        # Current-version meaning:
        # available=True only when online and there is no active delivery.
        #
        # IMPORTANT:
        # is_available=False DOES NOT prevent admin from assigning
        # more orders in this version.
        profile.is_available = bool(
            profile.is_online and active_count == 0
        )

        return active_count

    # ============================================================
    # AVAILABLE / ASSIGNABLE DELIVERY PARTNERS
    # ============================================================

    @staticmethod
    async def get_available_partners(
        db: AsyncSession,
    ) -> list[User]:
        """
        Current GramaGo version:

        Return every delivery partner who is:
        - DELIVERY_PARTNER
        - account active
        - approved
        - online

        DO NOT filter by profile.is_available.

        is_available=False now means the partner is busy / has active work,
        but admin may still assign additional orders.
        """

        result = await db.execute(
            select(User)
            .options(
                selectinload(User.delivery_profile)
            )
            .where(
                User.role == "DELIVERY_PARTNER",
                User.is_active.is_(True),
            )
            .order_by(
                User.full_name.asc()
            )
        )

        users = list(result.scalars().all())

        assignable: list[User] = []

        for user in users:
            profile = user.delivery_profile

            if profile is None:
                continue

            if not profile.is_approved:
                continue

            if not profile.is_online:
                continue

            # IMPORTANT:
            # Do not filter on profile.is_available.
            # Busy partners are still assignable in the current version.
            assignable.append(user)

        return assignable

    # ============================================================
    # GET ORDER
    # ============================================================

    @staticmethod
    async def get_order(
        db: AsyncSession,
        order_id: int,
    ) -> Order:

        result = await db.execute(
            select(Order)
            .options(
                selectinload(
                    Order.delivery_assignments
                )
            )
            .where(
                Order.id == order_id
            )
        )

        order = result.scalar_one_or_none()

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        return order

    # ============================================================
    # GET DELIVERY PARTNER
    # ============================================================

    @staticmethod
    async def get_delivery_partner(
        db: AsyncSession,
        partner_id: int,
    ) -> User:

        result = await db.execute(
            select(User)
            .options(
                selectinload(
                    User.delivery_profile
                )
            )
            .where(
                User.id == partner_id,
                User.role == "DELIVERY_PARTNER",
            )
        )

        partner = result.scalar_one_or_none()

        if partner is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery partner not found",
            )

        return partner

    # ============================================================
    # ASSIGN ORDER
    # ============================================================

    @staticmethod
    async def assign_order(
        db: AsyncSession,
        order_id: int,
        partner_id: int,
        admin_user: User,
        delivery_note: str | None = None,
    ) -> DeliveryAssignment:

        # --------------------------------------------------------
        # LOAD ORDER
        # --------------------------------------------------------

        order = await DeliveryAssignmentService.get_order(
            db,
            order_id,
        )

        # --------------------------------------------------------
        # VALID ORDER STATUS
        # --------------------------------------------------------

        allowed_statuses = {
            "PACKED",
            "READY_FOR_PICKUP",
        }

        if order.order_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Order must be packed or ready "
                    "for pickup before assignment"
                ),
            )

        # --------------------------------------------------------
        # PREVENT SAME ORDER FROM HAVING TWO ACTIVE ASSIGNMENTS
        # --------------------------------------------------------

        for existing_assignment in order.delivery_assignments:
            if existing_assignment.status in ACTIVE_DELIVERY_STATUSES:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Order already has an active "
                        "delivery assignment"
                    ),
                )

        # --------------------------------------------------------
        # LOAD PARTNER
        # --------------------------------------------------------

        partner = await DeliveryAssignmentService.get_delivery_partner(
            db,
            partner_id,
        )

        profile = partner.delivery_profile

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery partner profile not found",
            )

        # --------------------------------------------------------
        # PARTNER VALIDATION
        # --------------------------------------------------------

        if not partner.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery partner account is inactive",
            )

        if not profile.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery partner is not approved",
            )

        if not profile.is_online:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery partner is offline",
            )

        # IMPORTANT:
        # We intentionally DO NOT check profile.is_available here.
        #
        # A partner may already have active deliveries and still receive
        # additional assignments in the current GramaGo version.

        # --------------------------------------------------------
        # CREATE ASSIGNMENT
        # --------------------------------------------------------

        assignment = DeliveryAssignment(
            order_id=order.id,
            delivery_partner_id=partner.id,
            status="ASSIGNED",
            delivery_note=(
                delivery_note.strip()
                if delivery_note
                else None
            ),
        )

        db.add(assignment)

        # --------------------------------------------------------
        # UPDATE ORDER
        # --------------------------------------------------------

        previous_status = order.order_status

        now = datetime.now(timezone.utc)

        order.order_status = "ASSIGNED"
        order.assigned_at = now

        # --------------------------------------------------------
        # PARTNER HAS ACTIVE WORK
        # --------------------------------------------------------

        profile.is_available = False

        # --------------------------------------------------------
        # ORDER STATUS HISTORY
        # --------------------------------------------------------

        history = OrderStatusHistory(
            order_id=order.id,
            from_status=previous_status,
            to_status="ASSIGNED",
            changed_by=admin_user.id,
            note=(
                f"Order assigned to delivery "
                f"partner {partner.full_name}"
            ),
        )

        db.add(history)

        # --------------------------------------------------------
        # COMMIT
        # --------------------------------------------------------

        # try:
        #     await db.commit()

        # except Exception:
        #     await db.rollback()
        #     raise

        # await db.refresh(assignment)

        # return assignment
        
        


        notification_service = (
            NotificationService(db)
        )

        customer_notification = (
            await notification_service
            .create_order_status_notification(
                user_id=order.user_id,
                order_id=order.id,
                order_number=order.order_number,
                order_status="ASSIGNED",
            )
        )

        await db.commit()
        

        await db.refresh(
            assignment
        )


        try:

            if customer_notification is not None:

                await notification_service.dispatch(
                    customer_notification
                )

        except Exception:

            logger.exception(
                "Unable to send customer "
                "assignment notification"
            )
        # ============================================================
        # DELIVERY ASSIGNMENT PUSH NOTIFICATION
        # ============================================================

        try:
            await DeliveryPushNotificationService.send_to_partner(
                db=db,

                partner_id=partner.id,

                title=(
                    "New Delivery Assigned"
                ),

                body=(
                    f"Order #{order.order_number} "
                    "has been assigned to you."
                ),

                data={
                    "type":
                        "DELIVERY_ASSIGNED",

                    "order_id":
                        str(order.id),

                    "order_number":
                        str(
                            order.order_number
                        ),
                },
            )

        except Exception:
            # Never fail the real assignment because
            # push notification failed.
            logger.exception(
                "Unable to send delivery assignment "
                "notification"
            )

        return assignment
