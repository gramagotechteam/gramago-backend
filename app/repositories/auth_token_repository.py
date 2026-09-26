from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_verification_token import (
    EmailVerificationToken,
)
from app.models.password_reset_token import (
    PasswordResetToken,
)


class AuthTokenRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # -----------------------------------
    # Password Reset
    # -----------------------------------

    async def get_password_reset_token(
        self,
        token_hash: str,
    ) -> PasswordResetToken | None:

        result = await self.db.execute(
            select(
                PasswordResetToken
            ).where(
                PasswordResetToken.token_hash
                == token_hash
            )
        )

        return result.scalar_one_or_none()


    async def invalidate_password_reset_tokens(
        self,
        user_id: int,
    ) -> None:

        await self.db.execute(
            update(
                PasswordResetToken
            )
            .where(
                PasswordResetToken.user_id
                == user_id,
                PasswordResetToken.used_at.is_(
                    None
                ),
            )
            .values(
                used_at=datetime.now(
                    timezone.utc
                )
            )
        )


    # -----------------------------------
    # Email Verification
    # -----------------------------------

    async def get_email_verification_token(
        self,
        token_hash: str,
    ) -> EmailVerificationToken | None:

        result = await self.db.execute(
            select(
                EmailVerificationToken
            ).where(
                EmailVerificationToken.token_hash
                == token_hash
            )
        )

        return result.scalar_one_or_none()


    async def invalidate_email_tokens(
        self,
        user_id: int,
    ) -> None:

        await self.db.execute(
            update(
                EmailVerificationToken
            )
            .where(
                EmailVerificationToken.user_id
                == user_id,
                EmailVerificationToken.used_at.is_(
                    None
                ),
            )
            .values(
                used_at=datetime.now(
                    timezone.utc
                )
            )
        )