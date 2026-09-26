# from datetime import datetime, timezone

# from sqlalchemy import select, update
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.phone_otp_session import (
#     PhoneOtpSession,
# )


# class PhoneOtpRepository:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db

#     # =========================================================
#     # CREATE
#     # =========================================================

#     async def create(
#         self,
#         session: PhoneOtpSession,
#     ) -> PhoneOtpSession:

#         self.db.add(session)

#         await self.db.flush()

#         return session

#     # =========================================================
#     # GET BY PUBLIC CHALLENGE ID
#     # =========================================================

#     async def get_by_challenge_id(
#         self,
#         challenge_id: str,
#     ) -> PhoneOtpSession | None:

#         result = await self.db.execute(
#             select(
#                 PhoneOtpSession
#             ).where(
#                 PhoneOtpSession.challenge_id
#                 == challenge_id
#             )
#         )

#         return result.scalar_one_or_none()

#     # =========================================================
#     # INVALIDATE OLD ACTIVE CHALLENGES
#     # =========================================================

#     async def invalidate_active(
#         self,
#         *,
#         user_id: int,
#         purpose: str,
#     ) -> None:

#         now = datetime.now(
#             timezone.utc
#         )

#         await self.db.execute(
#             update(
#                 PhoneOtpSession
#             )
#             .where(
#                 PhoneOtpSession.user_id
#                 == user_id,

#                 PhoneOtpSession.purpose
#                 == purpose,

#                 PhoneOtpSession.consumed_at.is_(
#                     None
#                 ),
#             )
#             .values(
#                 consumed_at=now
#             )
#         )









from datetime import datetime, timezone

from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.phone_otp_session import PhoneOtpSession


class PhoneOtpRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # =========================================================
    # CREATE
    # =========================================================

    async def create(
        self,
        session: PhoneOtpSession,
    ) -> PhoneOtpSession:

        self.db.add(session)

        await self.db.flush()

        return session

    # =========================================================
    # GET
    # =========================================================

    async def get_by_challenge_id(
        self,
        challenge_id: str,
    ) -> PhoneOtpSession | None:

        result = await self.db.execute(
            select(
                PhoneOtpSession
            ).where(
                PhoneOtpSession.challenge_id
                == challenge_id
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # GET + ROW LOCK
    #
    # Prevents two verification/resend requests from processing
    # the same OTP challenge simultaneously.
    # =========================================================

    async def get_by_challenge_id_for_update(
        self,
        challenge_id: str,
    ) -> PhoneOtpSession | None:

        result = await self.db.execute(
            select(
                PhoneOtpSession
            )
            .where(
                PhoneOtpSession.challenge_id
                == challenge_id
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()

    # =========================================================
    # INVALIDATE ACTIVE CHALLENGES
    # =========================================================

    async def invalidate_active(
        self,
        *,
        user_id: int,
        purpose: str,
        exclude_id: int | None = None,
    ) -> None:

        query = (
            update(
                PhoneOtpSession
            )
            .where(
                PhoneOtpSession.user_id
                == user_id,

                PhoneOtpSession.purpose
                == purpose,

                PhoneOtpSession.consumed_at.is_(
                    None
                ),
            )
        )

        if exclude_id is not None:
            query = query.where(
                PhoneOtpSession.id
                != exclude_id
            )

        await self.db.execute(
            query.values(
                consumed_at=datetime.now(
                    timezone.utc
                )
            )
        )

    # =========================================================
    # COUNT RECENT SENDS
    #
    # Registration itself also counts as an OTP send.
    # =========================================================

    async def count_recent_sends(
        self,
        *,
        user_id: int,
        purpose: str,
        since: datetime,
    ) -> int:

        result = await self.db.execute(
            select(
                func.count(
                    PhoneOtpSession.id
                )
            ).where(
                PhoneOtpSession.user_id
                == user_id,

                PhoneOtpSession.purpose
                == purpose,

                PhoneOtpSession.created_at
                >= since,
            )
        )

        return int(
            result.scalar_one()
        )
        
        
        



    async def get_latest_active(
        self,
        *,
        user_id: int,
        purpose: str,
    ) -> PhoneOtpSession | None:

        result = await self.db.execute(
            select(
                PhoneOtpSession
            )
            .where(
                PhoneOtpSession.user_id
                == user_id,

                PhoneOtpSession.purpose
                == purpose,

                PhoneOtpSession.consumed_at.is_(
                    None
                ),
            )
            .order_by(
                PhoneOtpSession.created_at.desc()
            )
            .limit(1)
        )

        return result.scalar_one_or_none()