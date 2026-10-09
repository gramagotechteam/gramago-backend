from datetime import (
    datetime,
    timedelta,
    timezone,
)

from decimal import Decimal

from fastapi import (
    HTTPException,
    status,
)

from app.services.notification_service import (
    NotificationService,
)


from app.utils.phone import (
    format_indian_phone_e164,
)


from app.services.delivery_assignment_service import (
    DeliveryAssignmentService,
)


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.delivery_assignment import (
    DeliveryAssignment,
)
from app.models.order import Order
from app.models.order_status_history import (
    OrderStatusHistory,
)
from app.models.user import User

from app.core.otp_security import (
    generate_otp,
    hash_otp,
    verify_otp_hash,
)

from app.services.start_messaging_service import (
    StartMessagingError,
    StartMessagingService,
)

class DeliveryWorkflowService:

    OTP_EXPIRE_MINUTES = 10
    OTP_MAX_ATTEMPTS = 5


    # =========================================================
    # LOAD ACTIVE ASSIGNMENT
    # =========================================================

    @staticmethod
    async def get_assignment(
        db: AsyncSession,
        partner: User,
        order_id: int,
    ) -> DeliveryAssignment:

        result = await db.execute(
            select(DeliveryAssignment)
            .options(
                selectinload(
                    DeliveryAssignment.order
                ).selectinload(
                    Order.payment
                )
            )
            .where(
                DeliveryAssignment.order_id
                == order_id,

                DeliveryAssignment.delivery_partner_id
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Delivery assignment not found"
                ),
            )

        return assignment


    # =========================================================
    # HISTORY HELPER
    # =========================================================

    @staticmethod
    def add_history(
        db: AsyncSession,
        *,
        order: Order,
        partner: User,
        from_status: str,
        to_status: str,
        note: str,
    ):

        db.add(
            OrderStatusHistory(
                order_id=order.id,
                from_status=from_status,
                to_status=to_status,
                changed_by=partner.id,
                note=note,
            )
        )
        
        
        

    # =========================================================
    # CUSTOMER ORDER STATUS NOTIFICATION
    # =========================================================

    @staticmethod
    async def create_customer_status_notification(
        db: AsyncSession,
        *,
        order: Order,
        order_status: str,
    ):
        notification_service = (
            NotificationService(db)
        )

        notification = (
            await notification_service
            .create_order_status_notification(
                user_id=order.user_id,
                order_id=order.id,
                order_number=order.order_number,
                order_status=order_status,
            )
        )

        return (
            notification_service,
            notification,
        )


    # =========================================================
    # DISPATCH CUSTOMER NOTIFICATION AFTER COMMIT
    # =========================================================

    @staticmethod
    async def dispatch_customer_notification(
        notification_service,
        notification,
    ):

        if notification is None:
            return

        try:

            await notification_service.dispatch(
                notification
            )

        except Exception as exc:

            print(
                "CUSTOMER ORDER PUSH ERROR:",
                type(exc).__name__,
                str(exc),
            )
            
            

    @staticmethod
    async def accept(
        db: AsyncSession,
        partner: User,
        order_id: int,
    ) -> DeliveryAssignment:

        assignment = (
            await DeliveryWorkflowService
            .get_assignment(
                db,
                partner,
                order_id,
            )
        )

        if assignment.status != "ASSIGNED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Only an assigned delivery "
                    "can be accepted"
                ),
            )

        order = assignment.order

        now = datetime.now(
            timezone.utc
        )

        previous_status = (
            order.order_status
        )

        assignment.status = "ACCEPTED"
        assignment.accepted_at = now

        order.order_status = "ACCEPTED"

        DeliveryWorkflowService.add_history(
            db,
            order=order,
            partner=partner,
            from_status=previous_status,
            to_status="ACCEPTED",
            note=(
                "Delivery partner accepted "
                "the assigned order"
            ),
        )

        # await db.commit()
        # await db.refresh(assignment)

        # return assignment


        notification_service, customer_notification = (
            await DeliveryWorkflowService
            .create_customer_status_notification(
                db,
                order=order,
                order_status="ACCEPTED",
            )
        )

        await db.commit()

        await db.refresh(
            assignment
        )

        await DeliveryWorkflowService.dispatch_customer_notification(
            notification_service,
            customer_notification,
        )

        return assignment


    @staticmethod
    async def reject(
        db: AsyncSession,
        partner: User,
        order_id: int,
        reason: str,
    ) -> DeliveryAssignment:

        assignment = (
            await DeliveryWorkflowService
            .get_assignment(
                db,
                partner,
                order_id,
            )
        )

        if assignment.status != "ASSIGNED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Only an assigned delivery "
                    "can be rejected"
                ),
            )

        order = assignment.order

        profile = (
            partner.delivery_profile
        )

        now = datetime.now(
            timezone.utc
        )

        previous_status = (
            order.order_status
        )

        assignment.status = "REJECTED"
        assignment.rejected_at = now
        assignment.rejection_reason = (
            reason.strip()
        )

        # Order becomes assignable again.
        order.order_status = (
            "READY_FOR_PICKUP"
        )

        if profile:
            # profile.is_available = True
            await db.flush()

            # await DeliveryAssignment.sync_partner_availability(
            #     db,
            #     partner,
            # )
            await DeliveryAssignmentService.sync_partner_availability(
    db,
    partner,
)

        DeliveryWorkflowService.add_history(
            db,
            order=order,
            partner=partner,
            from_status=previous_status,
            to_status="READY_FOR_PICKUP",
            note=(
                "Delivery assignment rejected. "
                f"Reason: {reason.strip()}"
            ),
        )


        notification_service, customer_notification = (
            await DeliveryWorkflowService
            .create_customer_status_notification(
                db,
                order=order,
                order_status="READY_FOR_PICKUP",
            )
        )
        
        await db.commit()
        await db.refresh(assignment)
        
        await DeliveryWorkflowService.dispatch_customer_notification(
    notification_service,
    customer_notification,
)

        return assignment
    
    
    



    @staticmethod
    async def mark_picked_up(
        db: AsyncSession,
        partner: User,
        order_id: int,
    ) -> DeliveryAssignment:

        assignment = (
            await DeliveryWorkflowService
            .get_assignment(
                db,
                partner,
                order_id,
            )
        )

        if assignment.status != "ACCEPTED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Delivery must be accepted "
                    "before pickup"
                ),
            )

        order = assignment.order

        now = datetime.now(
            timezone.utc
        )

        previous_status = (
            order.order_status
        )

        assignment.status = "PICKED_UP"
        assignment.picked_up_at = now

        order.order_status = "PICKED_UP"
        order.picked_up_at = now

        DeliveryWorkflowService.add_history(
            db,
            order=order,
            partner=partner,
            from_status=previous_status,
            to_status="PICKED_UP",
            note=(
                "Order picked up by "
                "delivery partner"
            ),
        )

        # await db.commit()
        # await db.refresh(assignment)

        # return assignment


        notification_service, customer_notification = (
            await DeliveryWorkflowService
            .create_customer_status_notification(
                db,
                order=order,
                order_status="PICKED_UP",
            )
        )

        await db.commit()

        await db.refresh(
            assignment
        )

        await DeliveryWorkflowService.dispatch_customer_notification(
            notification_service,
            customer_notification,
        )

        return assignment
    
    
        


    @staticmethod
    async def start_delivery(
        db: AsyncSession,
        partner: User,
        order_id: int,
    ) -> DeliveryAssignment:

        assignment = (
            await DeliveryWorkflowService
            .get_assignment(
                db,
                partner,
                order_id,
            )
        )

        if assignment.status != "PICKED_UP":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Order must be picked up "
                    "before starting delivery"
                ),
            )

        order = assignment.order

        if not order.delivery_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Customer delivery phone "
                    "number is missing"
                ),
            )

        now = datetime.now(
            timezone.utc
        )

        otp = generate_otp()

        challenge_id = (
            f"delivery:{assignment.id}"
        )

        otp_hash_value = hash_otp(
            challenge_id=challenge_id,
            otp=otp,
        )
        try:
            sms_phone = format_indian_phone_e164(
                order.delivery_phone
            )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Customer delivery phone number "
                    "is invalid"
                ),
            )
            
        
        # =========================================================
        # SEND OTP
        # =========================================================

        try:
            await StartMessagingService.send_otp(
                phone=sms_phone,
                otp=otp,
                idempotency_key=(
                    f"delivery-{assignment.id}-"
                    f"{int(now.timestamp())}"
                ),
            )

        except StartMessagingError as exc:

            await db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "Unable to send delivery OTP. "
                    "Please try again."
                ),
            ) from exc

        previous_status = (
            order.order_status
        )

        assignment.delivery_otp_hash = (
            otp_hash_value
        )

        assignment.delivery_otp_expires_at = (
            now
            + timedelta(
                minutes=(
                    DeliveryWorkflowService
                    .OTP_EXPIRE_MINUTES
                )
            )
        )

        assignment.delivery_otp_attempts = 0

        assignment.status = (
            "OUT_FOR_DELIVERY"
        )

        assignment.out_for_delivery_at = (
            now
        )

        order.order_status = (
            "OUT_FOR_DELIVERY"
        )

        order.out_for_delivery_at = (
            now
        )

        DeliveryWorkflowService.add_history(
            db,
            order=order,
            partner=partner,
            from_status=previous_status,
            to_status="OUT_FOR_DELIVERY",
            note=(
                "Delivery started and customer "
                "delivery OTP was sent"
            ),
        )
        
        notification_service, customer_notification = (
    await DeliveryWorkflowService
    .create_customer_status_notification(
        db,
        order=order,
        order_status="OUT_FOR_DELIVERY",
    )
)

        await db.commit()

        await db.refresh(
            assignment
        )
        
        await DeliveryWorkflowService.dispatch_customer_notification(
    notification_service,
    customer_notification,
)

        return assignment







    @staticmethod
    async def complete_delivery(
        db: AsyncSession,
        partner: User,
        order_id: int,
        otp: str,
        cod_collected_amount: Decimal | None,
    ) -> DeliveryAssignment:

        assignment = (
            await DeliveryWorkflowService
            .get_assignment(
                db,
                partner,
                order_id,
            )
        )

        if (
            assignment.status
            != "OUT_FOR_DELIVERY"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Order is not currently "
                    "out for delivery"
                ),
            )

        now = datetime.now(
            timezone.utc
        )

        # =========================================================
        # OTP EXISTS
        # =========================================================

        if (
            not assignment.delivery_otp_hash
            or
            not assignment.delivery_otp_expires_at
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery OTP not available",
            )

        # =========================================================
        # EXPIRED
        # =========================================================

        if (
            assignment.delivery_otp_expires_at
            <= now
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Delivery OTP expired"
                ),
            )

        # =========================================================
        # ATTEMPT LIMIT
        # =========================================================

        if (
            assignment.delivery_otp_attempts
            >=
            DeliveryWorkflowService
            .OTP_MAX_ATTEMPTS
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many incorrect OTP attempts"
                ),
            )

        # =========================================================
        # VERIFY OTP
        # =========================================================

        challenge_id = (
            f"delivery:{assignment.id}"
        )

        valid = verify_otp_hash(
            challenge_id=challenge_id,
            otp=otp.strip(),
            expected_hash=(
                assignment.delivery_otp_hash
            ),
        )

        if not valid:

            assignment.delivery_otp_attempts += 1

            await db.commit()

            attempts_left = max(
                0,
                (
                    DeliveryWorkflowService
                    .OTP_MAX_ATTEMPTS
                    -
                    assignment
                    .delivery_otp_attempts
                ),
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Incorrect OTP. "
                    f"{attempts_left} attempts remaining."
                ),
            )

        order = assignment.order
        payment = order.payment

        # =========================================================
        # COD CHECK
        # =========================================================

        payment_method = (
            payment.method.upper().strip()
            if payment and payment.method
            else ""
        )

        is_cod = payment_method in {
            "COD",
            "CASH_ON_DELIVERY",
            "CASH ON DELIVERY",
        }

        if is_cod:

            expected_amount = Decimal(
                str(order.total_amount)
            )

            if cod_collected_amount is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "COD collected amount is required"
                    ),
                )

            if (
                Decimal(
                    str(cod_collected_amount)
                )
                != expected_amount
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"COD amount must be "
                        f"{expected_amount}"
                    ),
                )

            assignment.cod_collected_amount = (
                cod_collected_amount
            )

            assignment.cod_collected_at = (
                now
            )

            if payment:
                payment.status = "PAID"
                payment.paid_at = now

            order.payment_status = "PAID"

        # =========================================================
        # COMPLETE
        # =========================================================

        previous_status = (
            order.order_status
        )

        assignment.delivery_otp_verified_at = (
            now
        )

        assignment.status = "DELIVERED"
        assignment.delivered_at = now

        order.order_status = "DELIVERED"
        order.delivered_at = now

        # Make partner free for another order.
        profile = (
            partner.delivery_profile
        )

        if profile:
            # profile.is_available = True
            await db.flush()

            await DeliveryAssignmentService.sync_partner_availability(
                db,
                partner,
            )

        DeliveryWorkflowService.add_history(
            db,
            order=order,
            partner=partner,
            from_status=previous_status,
            to_status="DELIVERED",
            note=(
                "Order delivered successfully "
                "after customer OTP verification"
            ),
        )

        notification_service, customer_notification = (
    await DeliveryWorkflowService
    .create_customer_status_notification(
        db,
        order=order,
        order_status="DELIVERED",
    )
)
        
        await db.commit()
        await db.refresh(assignment)
        await DeliveryWorkflowService.dispatch_customer_notification(
    notification_service,
    customer_notification,
)

        return assignment
    
    
    
    
    



    @staticmethod
    async def resend_delivery_otp(
        db: AsyncSession,
        partner: User,
        order_id: int,
    ) -> DeliveryAssignment:

        assignment = (
            await DeliveryWorkflowService
            .get_assignment(
                db,
                partner,
                order_id,
            )
        )

        if (
            assignment.status
            != "OUT_FOR_DELIVERY"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Delivery OTP can only be resent "
                    "while order is out for delivery"
                ),
            )

        order = assignment.order

        if not order.delivery_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Customer delivery phone "
                    "number is missing"
                ),
            )

        now = datetime.now(
            timezone.utc
        )

        # =========================================================
        # BASIC COOLDOWN
        # =========================================================

        if assignment.delivery_otp_sent_at:

            seconds_since_last_send = (
                now
                - assignment.delivery_otp_sent_at
            ).total_seconds()

            if seconds_since_last_send < 30:

                seconds_left = int(
                    30 - seconds_since_last_send
                )

                raise HTTPException(
                    status_code=(
                        status.HTTP_429_TOO_MANY_REQUESTS
                    ),
                    detail=(
                        f"Please wait {seconds_left} seconds "
                        f"before requesting another OTP"
                    ),
                )

        # if (
        #     assignment.delivery_otp_expires_at
        #     and
        #     assignment.delivery_otp_expires_at > now
        # ):
        #     # Optional small cooldown.
        #     # Keeps resend from being spammed repeatedly.
        #     pass

        otp = generate_otp()

        challenge_id = (
            f"delivery:{assignment.id}"
        )

        otp_hash_value = hash_otp(
            challenge_id=challenge_id,
            otp=otp,
        )

        # =========================================================
        # FORMAT PHONE
        # =========================================================

        try:
            sms_phone = (
                format_indian_phone_e164(
                    order.delivery_phone
                )
            )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Customer delivery phone "
                    "number is invalid"
                ),
            )

        # =========================================================
        # SEND OTP
        # =========================================================

        try:
            await StartMessagingService.send_otp(
                phone=sms_phone,
                otp=otp,
                idempotency_key=(
                    f"delivery-resend-"
                    f"{assignment.id}-"
                    f"{int(now.timestamp())}"
                ),
            )

        except StartMessagingError as exc:

            await db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "Unable to resend delivery OTP. "
                    "Please try again."
                ),
            ) from exc

        # =========================================================
        # REPLACE OLD OTP
        # =========================================================

        assignment.delivery_otp_hash = (
            otp_hash_value
        )

        assignment.delivery_otp_expires_at = (
            now
            + timedelta(
                minutes=(
                    DeliveryWorkflowService
                    .OTP_EXPIRE_MINUTES
                )
            )
        )

        assignment.delivery_otp_attempts = 0

        await db.commit()
        await db.refresh(
            assignment
        )

        return assignment
        
        






    @staticmethod
    async def mark_failed(
        db: AsyncSession,
        partner: User,
        order_id: int,
        reason: str,
    ) -> DeliveryAssignment:

        assignment = (
            await DeliveryWorkflowService
            .get_assignment(
                db,
                partner,
                order_id,
            )
        )

        allowed_statuses = {
            "ACCEPTED",
            "PICKED_UP",
            "OUT_FOR_DELIVERY",
        }

        if assignment.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Delivery cannot be marked failed "
                    "from its current status"
                ),
            )

        order = assignment.order

        profile = (
            partner.delivery_profile
        )

        now = datetime.now(
            timezone.utc
        )

        previous_status = (
            order.order_status
        )

        assignment.status = (
            "FAILED"
        )

        assignment.failed_at = (
            now
        )

        assignment.failure_reason = (
            reason.strip()
        )

        order.order_status = (
            "DELIVERY_FAILED"
        )

        # Clear OTP so it cannot later be used.
        assignment.delivery_otp_hash = None
        assignment.delivery_otp_expires_at = None
        assignment.delivery_otp_attempts = 0

        if profile:
            # profile.is_available = True
            await db.flush()

            await DeliveryAssignmentService.sync_partner_availability(
                db,
                partner,
            )

        DeliveryWorkflowService.add_history(
            db,
            order=order,
            partner=partner,
            from_status=previous_status,
            to_status="DELIVERY_FAILED",
            note=(
                "Delivery failed. "
                f"Reason: {reason.strip()}"
            ),
        )
        
        notification_service, customer_notification = (
    await DeliveryWorkflowService
    .create_customer_status_notification(
        db,
        order=order,
        order_status="DELIVERY_FAILED",
    )
)

        await db.commit()
        await db.refresh(
            assignment
        )

        await DeliveryWorkflowService.dispatch_customer_notification(
    notification_service,
    customer_notification,
)

        return assignment


