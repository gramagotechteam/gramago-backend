# # import asyncio

# # from firebase_admin import messaging

# # from sqlalchemy.ext.asyncio import (
# #     AsyncSession,
# # )

# # from app.core.firebase import (
# #     firebase_is_ready,
# # )

# # from app.repositories.device_token_repository import (
# #     DeviceTokenRepository,
# # )


# # class PushNotificationService:

# #     def __init__(
# #         self,
# #         db: AsyncSession,
# #     ):

# #         self.db = db

# #         self.devices = (
# #             DeviceTokenRepository(
# #                 db
# #             )
# #         )


# #     # =========================================================
# #     # SEND TO USER
# #     # =========================================================

# #     async def send_to_user(
# #         self,
# #         *,
# #         user_id: int,
# #         title: str,
# #         body: str,
# #         data: dict | None = None,
# #         image_url: str | None = None,
# #         channel_id: str = "gramago_general",
# #     ) -> dict:

# #         if not firebase_is_ready():

# #             return {
# #                 "success": False,
# #                 "sent": 0,
# #                 "failed": 0,
# #                 "reason":
# #                     "Firebase is not initialized",
# #             }


# #         devices = (
# #             await self.devices
# #             .get_active_for_user(
# #                 user_id
# #             )
# #         )


# #         if not devices:

# #             return {
# #                 "success": True,
# #                 "sent": 0,
# #                 "failed": 0,
# #                 "reason":
# #                     "No active devices",
# #             }


# #         firebase_data = (
# #             self._prepare_data(
# #                 data or {}
# #             )
# #         )


# #         sent = 0

# #         failed = 0


# #         for device in devices:

# #             message = messaging.Message(

# #                 token=device.fcm_token,


# #                 notification=(
# #                     messaging.Notification(

# #                         title=title,

# #                         body=body,

# #                         image=image_url,
# #                     )
# #                 ),


# #                 data=firebase_data,


# #                 android=(
# #                     messaging.AndroidConfig(

# #                         priority="high",

# #                         notification=(
# #                             messaging.AndroidNotification(

# #                                 channel_id=(
# #                                     channel_id
# #                                 ),

# #                                 sound="default",
# #                             )
# #                         ),
# #                     )
# #                 ),
# #             )


# #             try:

# #                 # firebase-admin is synchronous.
# #                 # Don't block FastAPI event loop.
# #                 await asyncio.to_thread(
# #                     messaging.send,
# #                     message,
# #                 )


# #                 sent += 1


# #             except (
# #                 messaging.UnregisteredError,
# #             ):

# #                 failed += 1


# #                 await self.devices.deactivate_by_token(
# #                     device.fcm_token
# #                 )


# #             except Exception as exc:

# #                 failed += 1


# #                 print(
# #                     "FCM SEND ERROR:",
# #                     type(exc).__name__,
# #                     str(exc),
# #                 )


# #         await self.db.commit()


# #         return {
# #             "success": (
# #                 sent > 0
# #                 or failed == 0
# #             ),
# #             "sent": sent,
# #             "failed": failed,
# #         }


# #     # =========================================================
# #     # DATA MUST BE STRING -> STRING FOR FCM
# #     # =========================================================

# #     def _prepare_data(
# #         self,
# #         data: dict,
# #     ) -> dict[str, str]:

# #         result: dict[str, str] = {}


# #         for key, value in data.items():

# #             if value is None:
# #                 continue


# #             if isinstance(
# #                 value,
# #                 bool,
# #             ):

# #                 result[str(key)] = (
# #                     "true"
# #                     if value
# #                     else "false"
# #                 )

# #             else:

# #                 result[str(key)] = str(
# #                     value
# #                 )


# #         return result










# import asyncio

# from firebase_admin import (
#     exceptions as firebase_exceptions,
#     messaging,
# )

# from sqlalchemy.ext.asyncio import (
#     AsyncSession,
# )

# from app.core.firebase import (
#     firebase_is_ready,
# )

# from app.repositories.device_token_repository import (
#     DeviceTokenRepository,
# )


# class PushNotificationService:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):

#         self.db = db

#         self.devices = (
#             DeviceTokenRepository(
#                 db
#             )
#         )


#     # =========================================================
#     # SEND PUSH TO ALL ACTIVE DEVICES OF ONE USER
#     # =========================================================

#     async def send_to_user(
#         self,
#         *,
#         user_id: int,
#         title: str,
#         body: str,
#         data: dict | None = None,
#         image_url: str | None = None,
#         channel_id: str = "gramago_general",
#     ) -> dict:

#         # -----------------------------------------------------
#         # Firebase must be initialized
#         # -----------------------------------------------------

#         if not firebase_is_ready():

#             return {
#                 "success": False,
#                 "sent": 0,
#                 "failed": 0,
#                 "reason":
#                     "Firebase is not initialized",
#             }


#         # -----------------------------------------------------
#         # Get active device tokens
#         # -----------------------------------------------------

#         devices = (
#             await self.devices
#             .get_active_for_user(
#                 user_id
#             )
#         )


#         if not devices:

#             return {
#                 "success": True,
#                 "sent": 0,
#                 "failed": 0,
#                 "reason":
#                     "No active devices",
#             }


#         # -----------------------------------------------------
#         # FCM data payload requires string values
#         # -----------------------------------------------------

#         firebase_data = (
#             self._prepare_data(
#                 data or {}
#             )
#         )


#         sent = 0

#         failed = 0

#         invalid_tokens = 0


#         # =====================================================
#         # SEND TO EACH REGISTERED DEVICE
#         # =====================================================

#         for device in devices:

#             token = (
#                 device.fcm_token
#                 .strip()
#             )


#             # -------------------------------------------------
#             # Basic protection against bad stored values
#             # -------------------------------------------------

#             if not token:

#                 failed += 1

#                 invalid_tokens += 1

#                 await self.devices.deactivate_by_token(
#                     device.fcm_token
#                 )

#                 continue


#             print(
#                 "FCM SEND:",
#                 f"user={user_id}",
#                 f"device_id={device.id}",
#                 f"token_length={len(token)}",
#                 f"token_start={token[:10]}...",
#             )


#             # =================================================
#             # FIREBASE MESSAGE
#             # =================================================

#             message = messaging.Message(

#                 token=token,


#                 notification=(
#                     messaging.Notification(

#                         title=title,

#                         body=body,

#                         image=image_url,
#                     )
#                 ),


#                 data=firebase_data,


#                 android=(
#                     messaging.AndroidConfig(

#                         priority="high",

#                         notification=(
#                             messaging.AndroidNotification(

#                                 channel_id=(
#                                     channel_id
#                                 ),

#                                 sound="default",
#                             )
#                         ),
#                     )
#                 ),
#             )


#             # =================================================
#             # SEND MESSAGE
#             # =================================================

#             try:

#                 # Firebase Admin SDK messaging.send()
#                 # is synchronous.
#                 #
#                 # Running it with asyncio.to_thread()
#                 # prevents blocking FastAPI's event loop.

#                 message_id = (
#                     await asyncio.to_thread(
#                         messaging.send,
#                         message,
#                     )
#                 )


#                 sent += 1


#                 print(
#                     "FCM SEND SUCCESS:",
#                     f"device_id={device.id}",
#                     f"message_id={message_id}",
#                 )


#             # =================================================
#             # TOKEN NO LONGER REGISTERED
#             # =================================================

#             except messaging.UnregisteredError as exc:

#                 failed += 1

#                 invalid_tokens += 1


#                 print(
#                     "FCM TOKEN UNREGISTERED:",
#                     f"device_id={device.id}",
#                     str(exc),
#                 )


#                 await self.devices.deactivate_by_token(
#                     token
#                 )


#             # =================================================
#             # INVALID REGISTRATION TOKEN
#             # =================================================

#             except (
#                 firebase_exceptions
#                 .InvalidArgumentError
#             ) as exc:

#                 failed += 1


#                 error_message = (
#                     str(exc)
#                 )


#                 print(
#                     "FCM INVALID ARGUMENT:",
#                     f"device_id={device.id}",
#                     error_message,
#                 )


#                 # Only deactivate if Firebase explicitly
#                 # says the registration token itself is bad.
#                 #
#                 # We do not want to deactivate valid tokens
#                 # because of some unrelated payload problem.

#                 lowered = (
#                     error_message.lower()
#                 )


#                 if (
#                     "registration token"
#                     in lowered
#                     or
#                     "registration-token"
#                     in lowered
#                 ):

#                     invalid_tokens += 1


#                     print(
#                         "FCM TOKEN DEACTIVATED:",
#                         f"device_id={device.id}",
#                     )


#                     await self.devices.deactivate_by_token(
#                         token
#                     )


#             # =================================================
#             # OTHER FIREBASE ERRORS
#             # =================================================

#             except Exception as exc:

#                 failed += 1


#                 print(
#                     "FCM SEND ERROR:",
#                     f"device_id={device.id}",
#                     type(exc).__name__,
#                     str(exc),
#                 )


#         # =====================================================
#         # SAVE ANY TOKEN DEACTIVATIONS
#         # =====================================================

#         await self.db.commit()


#         # =====================================================
#         # RESPONSE
#         # =====================================================

#         return {

#             "success": (
#                 sent > 0
#             ),

#             "sent": sent,

#             "failed": failed,

#             "invalid_tokens_deactivated":
#                 invalid_tokens,

#             "total_devices":
#                 len(devices),
#         }


#     # =========================================================
#     # PREPARE FCM DATA
#     #
#     # Firebase data values must be strings.
#     # =========================================================

#     def _prepare_data(
#         self,
#         data: dict,
#     ) -> dict[str, str]:

#         result: dict[str, str] = {}


#         for key, value in data.items():

#             if value is None:

#                 continue


#             # -------------------------------------------------
#             # Boolean
#             # -------------------------------------------------

#             if isinstance(
#                 value,
#                 bool,
#             ):

#                 result[
#                     str(key)
#                 ] = (
#                     "true"
#                     if value
#                     else "false"
#                 )


#             # -------------------------------------------------
#             # Everything else
#             # -------------------------------------------------

#             else:

#                 result[
#                     str(key)
#                 ] = str(
#                     value
#                 )


#         return result














import asyncio

from firebase_admin import (
    exceptions as firebase_exceptions,
    messaging,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.core.firebase import (
    firebase_is_ready,
)

from app.repositories.device_token_repository import (
    DeviceTokenRepository,
)


class PushNotificationService:

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.db = db

        self.devices = (
            DeviceTokenRepository(
                db
            )
        )


    # =========================================================
    # PERSONAL PUSH
    #
    # Order / delivery / account notifications.
    # =========================================================

    async def send_to_user(
        self,
        *,
        user_id: int,
        title: str,
        body: str,
        data: dict | None = None,
        image_url: str | None = None,
        channel_id: str = "gramago_general",
    ) -> dict:

        devices = (
            await self.devices
            .get_active_for_user(
                user_id
            )
        )


        return await self._send_to_devices(

            devices=devices,

            title=title,

            body=body,

            data=data,

            image_url=image_url,

            channel_id=channel_id,
        )


    # =========================================================
    # PUBLIC BROADCAST
    #
    # New products / price drops / offers / promotions.
    #
    # Includes:
    # - anonymous devices
    # - logged-in devices
    # =========================================================

    async def send_public(
        self,
        *,
        title: str,
        body: str,
        data: dict | None = None,
        image_url: str | None = None,
        channel_id: str = "gramago_general",
    ) -> dict:

        devices = (
            await self.devices
            .get_active_marketing_devices()
        )


        return await self._send_to_devices(

            devices=devices,

            title=title,

            body=body,

            data=data,

            image_url=image_url,

            channel_id=channel_id,
        )


    # =========================================================
    # COMMON DELIVERY ENGINE
    # =========================================================

    async def _send_to_devices(
        self,
        *,
        devices,
        title: str,
        body: str,
        data: dict | None,
        image_url: str | None,
        channel_id: str,
    ) -> dict:

        if not firebase_is_ready():

            return {

                "success": False,

                "sent": 0,

                "failed": 0,

                "reason":
                    "Firebase is not initialized",
            }


        if not devices:

            return {

                "success": True,

                "sent": 0,

                "failed": 0,

                "reason":
                    "No eligible devices",
            }


        firebase_data = (
            self._prepare_data(
                data or {}
            )
        )


        sent = 0

        failed = 0

        invalid_tokens = 0


        for device in devices:

            token = (
                device.fcm_token.strip()
            )


            if not token:

                failed += 1

                invalid_tokens += 1


                await self.devices.deactivate_by_token(
                    device.fcm_token
                )

                continue


            message = messaging.Message(

                token=token,


                notification=(
                    messaging.Notification(

                        title=title,

                        body=body,

                        image=image_url,
                    )
                ),


                data=firebase_data,


                android=(
                    messaging.AndroidConfig(

                        priority="high",

                        notification=(
                            messaging.AndroidNotification(

                                channel_id=(
                                    channel_id
                                ),

                                sound="default",
                            )
                        ),
                    )
                ),
            )


            try:

                message_id = (
                    await asyncio.to_thread(

                        messaging.send,

                        message,
                    )
                )


                sent += 1


                print(
                    "FCM SEND SUCCESS:",
                    f"device_id={device.id}",
                    f"message_id={message_id}",
                )


            except (
                messaging.UnregisteredError
            ) as exc:

                failed += 1

                invalid_tokens += 1


                print(
                    "FCM TOKEN UNREGISTERED:",
                    f"device_id={device.id}",
                    str(exc),
                )


                await self.devices.deactivate_by_token(
                    token
                )


            except (
                firebase_exceptions
                .InvalidArgumentError
            ) as exc:

                failed += 1


                error_message = (
                    str(exc)
                )


                print(
                    "FCM INVALID ARGUMENT:",
                    f"device_id={device.id}",
                    error_message,
                )


                lowered = (
                    error_message.lower()
                )


                if (
                    "registration token"
                    in lowered
                    or
                    "registration-token"
                    in lowered
                ):

                    invalid_tokens += 1


                    await self.devices.deactivate_by_token(
                        token
                    )


            except Exception as exc:

                failed += 1


                print(
                    "FCM SEND ERROR:",
                    f"device_id={device.id}",
                    type(exc).__name__,
                    str(exc),
                )


        await self.db.commit()


        return {

            "success":
                sent > 0,

            "sent":
                sent,

            "failed":
                failed,

            "invalid_tokens_deactivated":
                invalid_tokens,

            "total_devices":
                len(devices),
        }


    # =========================================================
    # FCM DATA VALUES MUST BE STRINGS
    # =========================================================

    def _prepare_data(
        self,
        data: dict,
    ) -> dict[str, str]:

        result: dict[str, str] = {}


        for key, value in data.items():

            if value is None:

                continue


            if isinstance(
                value,
                bool,
            ):

                result[
                    str(key)
                ] = (
                    "true"
                    if value
                    else "false"
                )

            else:

                result[
                    str(key)
                ] = str(
                    value
                )


        return result