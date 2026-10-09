# # app/services/delivery_push_notification_service.py

# from firebase_admin import messaging

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.delivery_firebase import (
#     initialize_delivery_firebase,
# )

# from app.services.delivery_device_token_service import (
#     DeliveryDeviceTokenService,
# )


# class DeliveryPushNotificationService:

#     @staticmethod
#     async def send_to_partner(
#         db: AsyncSession,
#         partner_id: int,
#         title: str,
#         body: str,
#         data: dict[str, str] | None = None,
#     ) -> None:

#         delivery_firebase_app = (
#             initialize_delivery_firebase()
#         )

#         tokens = (
#             await DeliveryDeviceTokenService
#             .get_active_tokens(
#                 db=db,
#                 user_id=partner_id,
#             )
#         )

#         if not tokens:
#             return

#         payload = {
#             str(key): str(value)
#             for key, value
#             in (data or {}).items()
#         }

#         for token in tokens:
#             try:
#                 message = messaging.Message(
#                     token=token,

#                     notification=
#                         messaging.Notification(
#                             title=title,
#                             body=body,
#                         ),

#                     data=payload,

#                     android=
#                         messaging.AndroidConfig(
#                             priority="high",

#                             notification=
#                                 messaging.AndroidNotification(
#                                     channel_id=
#                                         "delivery_assignments",

#                                     sound="default",
#                                 ),
#                         ),
#                 )

#                 messaging.send(
#                     message,
#                     app=delivery_firebase_app,
#                 )

#             except Exception as exc:
#                 print(
#                     "DELIVERY FCM ERROR:",
#                     exc,
#                 )




import asyncio
import logging

from firebase_admin import (
    messaging,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.core.delivery_firebase import (
    get_delivery_firebase_app,
)

from app.services.delivery_device_token_service import (
    DeliveryDeviceTokenService,
)


logger = logging.getLogger(
    __name__
)


class DeliveryPushNotificationService:

    # ============================================================
    # SEND TO DELIVERY PARTNER
    # ============================================================

    @staticmethod
    async def send_to_partner(
        db: AsyncSession,
        partner_id: int,
        title: str,
        body: str,
        data: dict[str, str] | None = None,
    ) -> None:
        

        # --------------------------------------------------------
        # Get partner devices
        # --------------------------------------------------------

        tokens = (
            await DeliveryDeviceTokenService
            .get_active_tokens(
                db=db,
                user_id=partner_id,
            )
        )

        if not tokens:
            logger.info(
                "No active delivery FCM tokens "
                "for partner %s",
                partner_id,
            )

            return


        
        print(
    "DELIVERY FCM PARTNER:",
    partner_id,
)

        print(
            "DELIVERY FCM TOKENS:",
            len(tokens),
        )

        # --------------------------------------------------------
        # Dedicated Delivery Firebase instance
        # --------------------------------------------------------

        delivery_firebase_app = (
            get_delivery_firebase_app()
        )

        # FCM data must be string:string
        payload = {
            str(key): str(value)
            for key, value
            in (data or {}).items()
        }

        # --------------------------------------------------------
        # Send each device
        # --------------------------------------------------------

        for token in tokens:

            try:
                message = messaging.Message(
                    token=token,

                    notification=(
                        messaging.Notification(
                            title=title,
                            body=body,
                        )
                    ),

                    data=payload,

                    android=(
                        messaging.AndroidConfig(
                            priority="high",

                            notification=(
                                messaging
                                .AndroidNotification(
                                    channel_id=(
                                        "delivery_assignments"
                                    ),

                                    sound="default",
                                )
                            ),
                        )
                    ),
                )

                # firebase-admin send() is synchronous.
                # Run it outside the async event loop.
                # message_id = await asyncio.to_thread(
                #     messaging.send,
                #     message,
                #     False,
                #     delivery_firebase_app,
                # )
                
                message_id = await asyncio.to_thread(
    lambda: messaging.send(
        message,
        app=delivery_firebase_app,
    )
)

                logger.info(
                    "Delivery FCM sent. "
                    "Partner=%s Message=%s",
                    partner_id,
                    message_id,
                )
                
                print(
    "DELIVERY FCM SENT:",
    message_id,
)

            except Exception:
                # Push notification failure must NEVER
                # rollback or fail an order assignment.
                logger.exception(
                    "Delivery FCM send failed. "
                    "Partner=%s",
                    partner_id,
                )