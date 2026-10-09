# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.device_token import DeviceToken
# from app.models.user import User


# class DeliveryDeviceTokenService:

#     # ============================================================
#     # REGISTER / UPDATE TOKEN
#     # ============================================================

#     @staticmethod
#     async def register_token(
#         db: AsyncSession,
#         user: User,
#         token: str,
#         platform: str = "ANDROID",
#     ) -> DeviceToken:

#         clean_token = token.strip()

#         clean_platform = (
#             platform.strip().upper()
#             if platform
#             else "ANDROID"
#         )

#         # --------------------------------------------------------
#         # Search globally by token
#         # --------------------------------------------------------

#         result = await db.execute(
#             select(
#                 DeviceToken
#             ).where(
#                 DeviceToken.token
#                 == clean_token
#             )
#         )

#         existing = (
#             result.scalar_one_or_none()
#         )

#         # --------------------------------------------------------
#         # Existing token
#         # --------------------------------------------------------

#         if existing is not None:

#             # The phone may previously have been logged into
#             # another account.
#             existing.user_id = user.id

#             existing.platform = (
#                 clean_platform
#             )

#             existing.is_active = True

#             await db.commit()

#             await db.refresh(
#                 existing
#             )

#             return existing

#         # --------------------------------------------------------
#         # New token
#         # --------------------------------------------------------

#         device_token = DeviceToken(
#             user_id=user.id,

#             token=clean_token,

#             platform=clean_platform,

#             is_active=True,
#         )

#         db.add(
#             device_token
#         )

#         await db.commit()

#         await db.refresh(
#             device_token
#         )

#         return device_token

#     # ============================================================
#     # DEACTIVATE TOKEN
#     # ============================================================

#     @staticmethod
#     async def deactivate_token(
#         db: AsyncSession,
#         user: User,
#         token: str,
#     ) -> None:

#         clean_token = (
#             token.strip()
#         )

#         result = await db.execute(
#             select(
#                 DeviceToken
#             ).where(
#                 DeviceToken.user_id
#                 == user.id,

#                 DeviceToken.token
#                 == clean_token,
#             )
#         )

#         device_token = (
#             result.scalar_one_or_none()
#         )

#         if device_token is None:
#             return

#         device_token.is_active = False

#         await db.commit()

#     # ============================================================
#     # GET ACTIVE TOKENS
#     # ============================================================

#     @staticmethod
#     async def get_active_tokens(
#         db: AsyncSession,
#         user_id: int,
#     ) -> list[str]:

#         result = await db.execute(
#             select(
#                 DeviceToken.token
#             ).where(
#                 DeviceToken.user_id
#                 == user_id,

#                 DeviceToken.is_active
#                 .is_(True),
#             )
#         )

#         return list(
#             result.scalars().all()
#         )
        
        
        


from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device_token import DeviceToken
from app.models.user import User


class DeliveryDeviceTokenService:

    # ============================================================
    # REGISTER / UPDATE DELIVERY FCM TOKEN
    # ============================================================

    @staticmethod
    async def register_token(
        db: AsyncSession,
        user: User,
        token: str,
        platform: str = "ANDROID",
    ) -> DeviceToken:

        clean_token = token.strip()

        clean_platform = (
            platform.strip().lower()
            if platform
            else "android"
        )

        # --------------------------------------------------------
        # FIND EXISTING TOKEN
        # --------------------------------------------------------

        result = await db.execute(
            select(
                DeviceToken
            ).where(
                DeviceToken.fcm_token
                == clean_token
            )
        )

        existing = (
            result.scalar_one_or_none()
        )

        # --------------------------------------------------------
        # TOKEN ALREADY EXISTS
        # --------------------------------------------------------

        if existing is not None:

            # Token may have previously belonged
            # to another logged-in account.
            existing.user_id = user.id

            existing.platform = (
                clean_platform
            )

            existing.is_active = True

            existing.last_seen_at = (
                datetime.now(
                    timezone.utc
                )
            )

            await db.commit()

            await db.refresh(
                existing
            )

            return existing

        # --------------------------------------------------------
        # CREATE NEW TOKEN
        # --------------------------------------------------------

        device_token = DeviceToken(
            user_id=user.id,

            fcm_token=clean_token,

            platform=clean_platform,

            is_active=True,

            allow_marketing=False,

            last_seen_at=datetime.now(
                timezone.utc
            ),
        )

        db.add(
            device_token
        )

        await db.commit()

        await db.refresh(
            device_token
        )

        return device_token

    # ============================================================
    # DEACTIVATE TOKEN
    # ============================================================

    @staticmethod
    async def deactivate_token(
        db: AsyncSession,
        user: User,
        token: str,
    ) -> None:

        clean_token = (
            token.strip()
        )

        result = await db.execute(
            select(
                DeviceToken
            ).where(
                DeviceToken.user_id
                == user.id,

                DeviceToken.fcm_token
                == clean_token,
            )
        )

        device_token = (
            result.scalar_one_or_none()
        )

        if device_token is None:
            return

        device_token.is_active = False

        device_token.last_seen_at = (
            datetime.now(
                timezone.utc
            )
        )

        await db.commit()

    # ============================================================
    # GET ACTIVE DELIVERY TOKENS
    # ============================================================

    @staticmethod
    async def get_active_tokens(
        db: AsyncSession,
        user_id: int,
    ) -> list[str]:

        result = await db.execute(
            select(
                DeviceToken.fcm_token
            ).where(
                DeviceToken.user_id
                == user_id,

                DeviceToken.is_active
                .is_(True),
            )
        )

        return list(
            result.scalars().all()
        )