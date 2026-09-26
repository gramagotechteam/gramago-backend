# from datetime import (
#     datetime,
#     timezone,
# )

# from sqlalchemy import (
#     select,
#     update,
# )

# from sqlalchemy.ext.asyncio import (
#     AsyncSession,
# )

# from app.models.device_token import (
#     DeviceToken,
# )


# class DeviceTokenRepository:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):

#         self.db = db


#     # =========================================================
#     # REGISTER / UPDATE
#     # =========================================================

#     async def register(
#         self,
#         *,
#         user_id: int,
#         token: str,
#         platform: str,
#         device_name: str | None = None,
#         app_version: str | None = None,
#     ) -> DeviceToken:
        
#         token = token.strip()

#         result = await self.db.execute(

#             select(DeviceToken)

#             .where(
#                 DeviceToken.fcm_token
#                 == token
#             )
#         )


#         device = (
#             result.scalar_one_or_none()
#         )


#         now = datetime.now(
#             timezone.utc
#         )


#         if device:

#             # Important:
#             # Token can move to another authenticated
#             # user on the same phone after logout/login.
#             device.user_id = user_id

#             device.platform = platform

#             device.device_name = (
#                 device_name
#             )

#             device.app_version = (
#                 app_version
#             )

#             device.is_active = True

#             device.last_seen_at = now


#             return device


#         device = DeviceToken(

#             user_id=user_id,

#             fcm_token=token,

#             platform=platform,

#             device_name=device_name,

#             app_version=app_version,

#             is_active=True,

#             last_seen_at=now,
#         )


#         self.db.add(
#             device
#         )


#         return device


#     # =========================================================
#     # USER ACTIVE TOKENS
#     # =========================================================

#     async def get_active_for_user(
#         self,
#         user_id: int,
#     ) -> list[DeviceToken]:

#         result = await self.db.execute(

#             select(DeviceToken)

#             .where(
#                 DeviceToken.user_id
#                 == user_id,

#                 DeviceToken.is_active
#                 .is_(True),
#             )
#         )


#         return list(
#             result.scalars().all()
#         )


#     # =========================================================
#     # DEACTIVATE SPECIFIC TOKEN
#     # =========================================================

#     async def deactivate_token(
#         self,
#         *,
#         user_id: int,
#         token: str,
#     ) -> None:

#         await self.db.execute(

#             update(DeviceToken)

#             .where(
#                 DeviceToken.user_id
#                 == user_id,

#                 DeviceToken.fcm_token
#                 == token,
#             )

#             .values(
#                 is_active=False,
#             )
#         )


#     # =========================================================
#     # INVALID FCM TOKEN
#     # =========================================================

#     async def deactivate_by_token(
#         self,
#         token: str,
#     ) -> None:

#         await self.db.execute(

#             update(DeviceToken)

#             .where(
#                 DeviceToken.fcm_token
#                 == token
#             )

#             .values(
#                 is_active=False,
#             )
#         )
















from datetime import (
    datetime,
    timezone,
)

from sqlalchemy import (
    select,
    update,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.device_token import (
    DeviceToken,
)


class DeviceTokenRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.db = db


    # =========================================================
    # PUBLIC / ANONYMOUS REGISTRATION
    #
    # Important:
    # If token already belongs to a logged-in user,
    # this method DOES NOT detach that user.
    # =========================================================

    async def register_public(
        self,
        *,
        token: str,
        platform: str,
        device_name: str | None = None,
        app_version: str | None = None,
    ) -> DeviceToken:

        token = token.strip()

        result = await self.db.execute(
            select(DeviceToken)
            .where(
                DeviceToken.fcm_token
                == token
            )
        )

        device = (
            result.scalar_one_or_none()
        )

        now = datetime.now(
            timezone.utc
        )


        if device:
            device.user_id = None

            device.platform = platform

            device.device_name = (
                device_name
            )

            device.app_version = (
                app_version
            )

            device.is_active = True

            device.last_seen_at = now

            return device


        device = DeviceToken(

            user_id=None,

            fcm_token=token,

            platform=platform,

            device_name=device_name,

            app_version=app_version,

            is_active=True,

            allow_marketing=True,

            last_seen_at=now,
        )


        self.db.add(
            device
        )

        await self.db.flush()

        return device


    # =========================================================
    # LINK DEVICE TO LOGGED-IN USER
    # =========================================================

    async def link_to_user(
        self,
        *,
        user_id: int,
        token: str,
    ) -> DeviceToken:

        token = token.strip()

        result = await self.db.execute(
            select(DeviceToken)
            .where(
                DeviceToken.fcm_token
                == token
            )
        )

        device = (
            result.scalar_one_or_none()
        )


        if not device:

            device = DeviceToken(

                user_id=user_id,

                fcm_token=token,

                platform="android",

                is_active=True,

                allow_marketing=True,

                last_seen_at=(
                    datetime.now(
                        timezone.utc
                    )
                ),
            )

            self.db.add(
                device
            )

            await self.db.flush()

            return device


        device.user_id = user_id

        device.is_active = True

        device.last_seen_at = (
            datetime.now(
                timezone.utc
            )
        )

        return device


    # =========================================================
    # LOGOUT
    #
    # Do NOT deactivate.
    # Device becomes anonymous.
    # =========================================================

    # async def detach_from_user(
    #     self,
    #     *,
    #     user_id: int,
    #     token: str,
    # ) -> None:

    #     token = token.strip()

    #     await self.db.execute(

    #         update(DeviceToken)

    #         .where(
    #             DeviceToken.user_id
    #             == user_id,

    #             DeviceToken.fcm_token
    #             == token,
    #         )

    #         .values(
    #             user_id=None,
    #             is_active=True,
    #             last_seen_at=(
    #                 datetime.now(
    #                     timezone.utc
    #                 )
    #             ),
    #         )
    #     )


    async def detach_from_user(
        self,
        *,
        user_id: int,
        token: str,
    ) -> None:

        token = token.strip()

        await self.db.execute(

            update(DeviceToken)

            .where(
                DeviceToken.user_id == user_id,
                DeviceToken.fcm_token == token,
            )

            .values(
                user_id=None,
                is_active=True,
                last_seen_at=datetime.now(
                    timezone.utc
                ),
            )
        )

    # =========================================================
    # PERSONAL USER TOKENS
    # =========================================================

    async def get_active_for_user(
        self,
        user_id: int,
    ) -> list[DeviceToken]:

        result = await self.db.execute(

            select(DeviceToken)

            .where(
                DeviceToken.user_id
                == user_id,

                DeviceToken.is_active
                .is_(True),
            )
        )


        return list(
            result.scalars().all()
        )


    # =========================================================
    # PUBLIC MARKETING TOKENS
    # =========================================================

    async def get_active_marketing_devices(
        self,
    ) -> list[DeviceToken]:

        result = await self.db.execute(

            select(DeviceToken)

            .where(
                DeviceToken.is_active
                .is_(True),

                DeviceToken.allow_marketing
                .is_(True),
            )
        )


        return list(
            result.scalars().all()
        )


    # =========================================================
    # CHANGE MARKETING PREFERENCE
    # =========================================================

    async def set_marketing_preference(
        self,
        *,
        token: str,
        allow_marketing: bool,
    ) -> None:

        token = token.strip()

        await self.db.execute(

            update(DeviceToken)

            .where(
                DeviceToken.fcm_token
                == token
            )

            .values(
                allow_marketing=(
                    allow_marketing
                ),
            )
        )


    # =========================================================
    # INVALID TOKEN
    # =========================================================

    async def deactivate_by_token(
        self,
        token: str,
    ) -> None:

        token = token.strip()

        await self.db.execute(

            update(DeviceToken)

            .where(
                DeviceToken.fcm_token
                == token
            )

            .values(
                is_active=False,
                user_id=None,
            )
        )