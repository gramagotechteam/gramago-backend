from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister


from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)

from sqlalchemy import select
from sqlalchemy.orm import selectinload



from app.core.otp_security import (
    generate_challenge_id,
    generate_idempotency_key,
    generate_otp,
    hash_otp,
    verify_otp_hash,
)


from app.core.otp_security import (
    generate_challenge_id,
    generate_idempotency_key,
    generate_otp,
    hash_otp,
)

from app.models.phone_otp_session import (
    PhoneOtpSession,
)

from app.repositories.phone_otp_repository import (
    PhoneOtpRepository,
)

from app.services.start_messaging_service import (
    StartMessagingError,
    StartMessagingService,
)

from app.utils.phone import (
    normalize_indian_phone,
)

import logging

from datetime import datetime, timedelta, timezone

from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_secure_token,
    hash_password,
    hash_token,
    verify_password,
)

from app.models.password_reset_token import (
    PasswordResetToken,
)

from app.models.email_verification_token import (
    EmailVerificationToken,
)

from app.repositories.auth_token_repository import (
    AuthTokenRepository,
)

from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

class AuthService:
    
    def __init__(
    self,
    db: AsyncSession,):
        
        self.db = db

        self.users = UserRepository(db)

        self.refresh_tokens = (
            RefreshTokenRepository(db)
        )
        
        self.auth_tokens = (
    AuthTokenRepository(db)
)
        
        self.phone_otps = (
    PhoneOtpRepository(db)
)

    # def __init__(self, db: AsyncSession):
    #     self.db = db
    #     self.users = UserRepository(db)

    # async def register(
    #     self,
    #     data: UserRegister,
    # ) -> User:

    #     phone = data.phone.strip()

    #     existing_phone = await self.users.get_by_phone(
    #         phone
    #     )

    #     if existing_phone:
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="Phone number already registered",
    #         )

    #     email = None

    #     if data.email:
    #         email = data.email.lower().strip()

    #         existing_email = (
    #             await self.users.get_by_email(
    #                 email
    #             )
    #         )

    #         if existing_email:
    #             raise HTTPException(
    #                 status_code=status.HTTP_409_CONFLICT,
    #                 detail="Email already registered",
    #             )

    #     user = User(
    #         full_name=data.full_name.strip(),
    #         phone=phone,
    #         email=email,
    #         password_hash=hash_password(
    #             data.password
    #         ),
    #         role="CUSTOMER",
    #         is_active=True,
    #         is_verified=False,
    #     )

    #     self.db.add(user)

    #     await self.db.commit()
    #     await self.db.refresh(user)


    #     return user




    async def register(
        self,
        data: UserRegister,
    ) -> dict:

        # =========================================================
        # NORMALIZE PHONE
        # =========================================================

        phone = normalize_indian_phone(
            data.phone
        )

        # =========================================================
        # CHECK PHONE
        # =========================================================

        existing_phone = (
            await self.users.get_by_phone(
                phone
            )
        )

        if existing_phone:

            if not existing_phone.is_verified:
                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "An account with this phone "
                        "number already exists and "
                        "is awaiting verification"
                    ),
                )

            raise HTTPException(
                status_code=(
                    status.HTTP_409_CONFLICT
                ),
                detail=(
                    "Phone number already registered"
                ),
            )

        # =========================================================
        # OPTIONAL EMAIL
        # =========================================================

        email = None

        if data.email:

            email = (
                str(data.email)
                .lower()
                .strip()
            )

            existing_email = (
                await self.users
                .get_by_email(
                    email
                )
            )

            if existing_email:
                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "Email already registered"
                    ),
                )

        # =========================================================
        # GENERATE OTP CHALLENGE
        # =========================================================

        otp = generate_otp()

        challenge_id = (
            generate_challenge_id()
        )

        idempotency_key = (
            generate_idempotency_key()
        )

        otp_hash_value = hash_otp(
            challenge_id=challenge_id,
            otp=otp,
        )

        now = datetime.now(
            timezone.utc
        )

        expires_at = (
            now
            + timedelta(
                seconds=(
                    settings
                    .OTP_EXPIRE_SECONDS
                )
            )
        )

        resend_available_at = (
            now
            + timedelta(
                seconds=(
                    settings
                    .OTP_RESEND_SECONDS
                )
            )
        )

        # =========================================================
        # CREATE USER + OTP SESSION
        # =========================================================
        #
        # We intentionally do not commit yet.
        #
        # User + OTP session must only become permanent
        # after StartMessaging accepts the SMS.
        # =========================================================

        try:

            user = User(
                full_name=(
                    data.full_name.strip()
                ),
                phone=phone,
                email=email,
                password_hash=(
                    hash_password(
                        data.password
                    )
                ),
                role="CUSTOMER",
                is_active=True,
                is_verified=False,
            )

            self.db.add(
                user
            )

            # We need user.id for the OTP FK.
            await self.db.flush()

            otp_session = PhoneOtpSession(
                challenge_id=challenge_id,
                user_id=user.id,
                purpose="REGISTRATION",
                phone=phone,
                otp_hash=otp_hash_value,
                provider_request_id=None,
                idempotency_key=(
                    idempotency_key
                ),
                attempts=0,
                expires_at=expires_at,
                resend_available_at=(
                    resend_available_at
                ),
            )

            await self.phone_otps.create(
                otp_session
            )

            # =====================================================
            # SEND OTP
            # =====================================================

            provider_request_id = (
                await StartMessagingService
                .send_otp(
                    phone=phone,
                    otp=otp,
                    idempotency_key=(
                        idempotency_key
                    ),
                )
            )

            otp_session.provider_request_id = (
                provider_request_id
            )

            # =====================================================
            # COMMIT ONLY AFTER PROVIDER ACCEPTS SMS
            # =====================================================

            await self.db.commit()

            await self.db.refresh(
                user
            )

            await self.db.refresh(
                otp_session
            )

        except StartMessagingError as exc:

            await self.db.rollback()

            logger.exception(
                "Registration OTP delivery failed"
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "Unable to send verification "
                    "code right now. Please try again."
                ),
            ) from exc

        except HTTPException:

            await self.db.rollback()

            raise

        except Exception:

            await self.db.rollback()

            logger.exception(
                "Registration failed"
            )

            raise

        # =========================================================
        # IMPORTANT
        # =========================================================
        #
        # Do not:
        # - return OTP
        # - log OTP
        # - issue access token
        # - issue refresh token
        #
        # OTP plaintext goes out of scope here.
        # =========================================================

        return {
            "verification_required": True,
            "challenge_id": (
                challenge_id
            ),
            "phone_masked": (
                self._mask_phone(
                    phone
                )
            ),
            "expires_in": (
                settings
                .OTP_EXPIRE_SECONDS
            ),
            "resend_in": (
                settings
                .OTP_RESEND_SECONDS
            ),
        }
        
        
        
        
    # async def login(
    #     self,
    #     identifier: str,
    #     password: str,
    # ):

    #     identifier = identifier.strip()

    #     if "@" in identifier:
    #         identifier = identifier.lower()

    #     user = await self.users.get_by_identifier(
    #         identifier
    #     )

    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Invalid credentials",
    #         )

    #     if not verify_password(
    #         password,
    #         user.password_hash,
    #     ):
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Invalid credentials",
    #         )

    #     if not user.is_active:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Account is disabled",
    #         )

    #     access_token = create_access_token(
    #         user_id=user.id,
    #         role=user.role,
    #     )

    #     refresh_token = create_refresh_token()

    #     refresh_record = RefreshToken(
    #         user_id=user.id,
    #         token_hash=hash_token(
    #             refresh_token
    #         ),
    #         expires_at=(
    #             datetime.now(timezone.utc)
    #             + timedelta(
    #                 days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    #             )
    #         ),
    #     )

    #     self.db.add(refresh_record)

    #     user.last_login_at = datetime.now(
    #         timezone.utc
    #     )

    #     await self.db.commit()
    #     await self.db.refresh(user)

    #     return {
    #         "access_token": access_token,
    #         "refresh_token": refresh_token,
    #         "token_type": "bearer",
    #         "expires_in": (
    #             settings.ACCESS_TOKEN_EXPIRE_MINUTES
    #             * 60
    #         ),
    #         "user": user,
    #     }
        
            
    async def login(
        self,
        identifier: str,
        password: str,
    ) -> dict:

        identifier = identifier.strip()

        # =========================================================
        # NORMALIZE IDENTIFIER
        # =========================================================

        if "@" in identifier:

            identifier = (
                identifier
                .lower()
                .strip()
            )

        else:

            try:
                identifier = (
                    normalize_indian_phone(
                        identifier
                    )
                )

            except HTTPException:

                # Don't expose whether the
                # phone format/account exists.
                raise HTTPException(
                    status_code=(
                        status.HTTP_401_UNAUTHORIZED
                    ),
                    detail="Invalid credentials",
                )

        # =========================================================
        # FIND USER
        # =========================================================

        user = (
            await self.users
            .get_by_identifier(
                identifier
            )
        )

        if not user:
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Invalid credentials",
            )

        # =========================================================
        # PASSWORD FIRST
        # =========================================================

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Invalid credentials",
            )

        # =========================================================
        # ACCOUNT STATUS
        # =========================================================

        if not user.is_active:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail="Account is disabled",
            )

        # =========================================================
        # PHONE VERIFICATION
        #
        # Registration-created customers must verify phone
        # before receiving any JWT.
        # =========================================================

        if (
            user.role == "CUSTOMER"
            and not user.is_verified
        ):

            verification = (
                await self
                ._start_login_verification(
                    user
                )
            )

            return {
                "authenticated": False,
                **verification,
            }

        # =========================================================
        # NORMAL VERIFIED LOGIN
        # =========================================================

        auth_data = (
            await self
            ._create_auth_session(
                user
            )
        )

        await self.db.commit()

        await self.db.refresh(
            user
        )

        return {
            "authenticated": True,
            "verification_required": False,
            **auth_data,
            "user": user,
        }
        
    




    async def verify_login_otp(
        self,
        *,
        challenge_id: str,
        otp: str,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        session = (
            await self.phone_otps
            .get_by_challenge_id_for_update(
                challenge_id.strip()
            )
        )

        if not session:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid or expired "
                    "verification code"
                ),
            )

        # =========================================================
        # PURPOSE
        # =========================================================

        if (
            session.purpose
            != "LOGIN_VERIFICATION"
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid verification "
                    "request"
                ),
            )

        # =========================================================
        # CONSUMED
        # =========================================================

        if session.consumed_at is not None:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Verification code is "
                    "no longer valid"
                ),
            )

        # =========================================================
        # EXPIRED
        # =========================================================

        if session.expires_at <= now:

            session.consumed_at = now

            await self.db.commit()

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Verification code expired. "
                    "Please request a new code."
                ),
            )

        # =========================================================
        # ATTEMPTS
        # =========================================================

        if (
            session.attempts
            >= settings.OTP_MAX_ATTEMPTS
        ):

            session.consumed_at = now

            await self.db.commit()

            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many incorrect attempts. "
                    "Please request a new code."
                ),
            )

        # =========================================================
        # CHECK OTP
        # =========================================================

        valid = verify_otp_hash(
            challenge_id=(
                session.challenge_id
            ),
            otp=otp.strip(),
            expected_hash=(
                session.otp_hash
            ),
        )

        if not valid:

            session.attempts += 1

            attempts_left = max(
                0,
                settings.OTP_MAX_ATTEMPTS
                - session.attempts,
            )

            if attempts_left == 0:
                session.consumed_at = now

            await self.db.commit()

            if attempts_left == 0:
                raise HTTPException(
                    status_code=(
                        status.HTTP_429_TOO_MANY_REQUESTS
                    ),
                    detail=(
                        "Too many incorrect attempts. "
                        "Please request a new code."
                    ),
                )

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    f"Incorrect verification code. "
                    f"{attempts_left} attempts remaining."
                ),
            )

        # =========================================================
        # USER
        # =========================================================

        user = await self.users.get_by_id(
            session.user_id
        )

        if not user:
            await self.db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail="Invalid verification request",
            )

        if not user.is_active:
            await self.db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail="Account is disabled",
            )

        # =========================================================
        # SUCCESS
        # =========================================================

        user.is_verified = True

        session.verified_at = now
        session.consumed_at = now

        await self.phone_otps.invalidate_active(
            user_id=user.id,
            purpose=(
                "LOGIN_VERIFICATION"
            ),
            exclude_id=session.id,
        )

        auth_data = (
            await self._create_auth_session(
                user
            )
        )

        await self.db.commit()

        await self.db.refresh(
            user
        )

        return {
            "authenticated": True,
            "verification_required": False,
            **auth_data,
            "user": user,
        }
        
        
    

    async def refresh(
    self,
    raw_refresh_token: str,):
        token_hash = hash_token(
            raw_refresh_token
        )

        token_record = (
            await self.refresh_tokens.get_by_hash(
                token_hash
            )
        )

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if token_record.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked",
            )

        now = datetime.now(timezone.utc)

        if token_record.expires_at <= now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
            )

        user = await self.users.get_by_id(
            token_record.user_id
        )

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user",
            )

        # Revoke old refresh token
        await self.refresh_tokens.revoke(
            token_record
        )

        # Generate new access token
        new_access_token = create_access_token(
            user_id=user.id,
            role=user.role,
        )

        # Generate new refresh token
        new_refresh_token = (
            create_refresh_token()
        )

        new_refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(
                new_refresh_token
            ),
            expires_at=(
                now
                + timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                )
            ),
        )

        self.db.add(
            new_refresh_record
        )

        await self.db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": (
                settings.ACCESS_TOKEN_EXPIRE_MINUTES
                * 60
            ),
        }
        
    
    
    
    
    async def logout(
    self,
    raw_refresh_token: str,):
        
        token_hash = hash_token(
            raw_refresh_token
        )

        token_record = (
            await self.refresh_tokens.get_by_hash(
                token_hash
            )
        )

        if not token_record:
            return

        if token_record.revoked_at is None:
            await self.refresh_tokens.revoke(
                token_record
            )

        await self.db.commit()
        
    
    
    
    async def logout_all(
    self,
    user_id: int,):
        await self.refresh_tokens.revoke_all_for_user(
            user_id
        )

        await self.db.commit()
        
        
    
    
    
    
    async def change_password(
    self,
    user: User,
    current_password: str,
    new_password: str,
    ):
        if not verify_password(
            current_password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        if verify_password(
            new_password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different",
            )

        user.password_hash = hash_password(
            new_password
        )

        await self.refresh_tokens.revoke_all_for_user(
            user.id
        )

        await self.db.commit()
        
    
    
    # async def forgot_password(
    # self,
    # email: str,) -> None:
        

    #     email = email.lower().strip()

    #     user = await self.users.get_by_email(
    #         email
    #     )

    #     # IMPORTANT:
    #     # Don't reveal whether account exists.

    #     if not user:
    #         return

    #     if not user.is_active:
    #         return

    #     await self.auth_tokens.invalidate_password_reset_tokens(
    #         user.id
    #     )

    #     raw_token = create_secure_token()

    #     token_record = PasswordResetToken(
    #         user_id=user.id,
    #         token_hash=hash_token(
    #             raw_token
    #         ),
    #         expires_at=(
    #             datetime.now(timezone.utc)
    #             + timedelta(
    #                 minutes=(
    #                     settings
    #                     .PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    #                 )
    #             )
    #         ),
    #     )

    #     self.db.add(token_record)

    #     await self.db.commit()

    #     try:

    #         await EmailService.send_password_reset(
    #             recipient=email,
    #             token=raw_token,
    #         )

    #     except Exception:

    #         logger.exception(
    #             "Password reset email failed"
    #         )
            
            
    async def forgot_password(
        self,
        identifier: str,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        identifier = identifier.strip()

        # =========================================================
        # NORMALIZE IDENTIFIER
        # =========================================================

        if "@" in identifier:

            lookup_identifier = (
                identifier
                .lower()
                .strip()
            )

        else:

            try:
                lookup_identifier = (
                    normalize_indian_phone(
                        identifier
                    )
                )

            except HTTPException:

                # Generic response.
                # Do not reveal account existence.
                return (
                    self
                    ._fake_password_reset_response()
                )

        # =========================================================
        # FIND USER
        # =========================================================

        user = (
            await self.users
            .get_by_identifier(
                lookup_identifier
            )
        )

        # IMPORTANT:
        # Do not reveal:
        # - account does not exist
        # - account disabled
        #
        # Same response format either way.
        if (
            not user
            or not user.is_active
        ):
            return (
                self
                ._fake_password_reset_response()
            )

        # =========================================================
        # REUSE ACTIVE PASSWORD RESET CHALLENGE
        #
        # Prevent repeated Forgot Password presses
        # from sending multiple SMS messages.
        # =========================================================

        existing = (
            await self.phone_otps
            .get_latest_active(
                user_id=user.id,
                purpose="PASSWORD_RESET",
            )
        )

        if existing:

            if (
                existing.expires_at > now
                and
                existing.attempts
                < settings.OTP_MAX_ATTEMPTS
            ):

                return {
                    "verification_required": True,
                    "challenge_id": (
                        existing.challenge_id
                    ),
                    "expires_in": max(
                        0,
                        int(
                            (
                                existing.expires_at
                                - now
                            ).total_seconds()
                        ),
                    ),
                    "resend_in": max(
                        0,
                        int(
                            (
                                existing
                                .resend_available_at
                                - now
                            ).total_seconds()
                        ),
                    ),
                }

        # =========================================================
        # MAX 3 SENDS / 5 MINUTES
        # =========================================================

        recent_count = (
            await self.phone_otps
            .count_recent_sends(
                user_id=user.id,
                purpose="PASSWORD_RESET",
                since=(
                    now
                    - timedelta(
                        minutes=5
                    )
                ),
            )
        )

        if recent_count >= 3:

            # Still don't expose account state.
            return (
                self
                ._fake_password_reset_response()
            )

        # =========================================================
        # GENERATE OTP
        # =========================================================

        otp = generate_otp()

        challenge_id = (
            generate_challenge_id()
        )

        idempotency_key = (
            generate_idempotency_key()
        )

        otp_session = PhoneOtpSession(
            challenge_id=challenge_id,

            user_id=user.id,

            purpose="PASSWORD_RESET",

            phone=user.phone,

            otp_hash=hash_otp(
                challenge_id=challenge_id,
                otp=otp,
            ),

            provider_request_id=None,

            idempotency_key=(
                idempotency_key
            ),

            attempts=0,

            expires_at=(
                now
                + timedelta(
                    seconds=(
                        settings
                        .OTP_EXPIRE_SECONDS
                    )
                )
            ),

            resend_available_at=(
                now
                + timedelta(
                    seconds=(
                        settings
                        .OTP_RESEND_SECONDS
                    )
                )
            ),
        )

        try:

            await self.phone_otps.create(
                otp_session
            )

            provider_request_id = (
                await StartMessagingService
                .send_otp(
                    phone=user.phone,
                    otp=otp,
                    idempotency_key=(
                        idempotency_key
                    ),
                )
            )

            otp_session.provider_request_id = (
                provider_request_id
            )

            await self.phone_otps.invalidate_active(
                user_id=user.id,
                purpose="PASSWORD_RESET",
                exclude_id=otp_session.id,
            )

            await self.db.commit()

        except StartMessagingError:

            await self.db.rollback()

            logger.exception(
                "Password reset OTP "
                "delivery failed"
            )

            # IMPORTANT:
            # Keep generic response so provider
            # failures cannot become an
            # account-enumeration signal.
            return (
                self
                ._fake_password_reset_response()
            )

        except Exception:

            await self.db.rollback()

            logger.exception(
                "Password reset request failed"
            )

            raise

        return {
            "verification_required": True,

            "challenge_id": (
                challenge_id
            ),

            "expires_in": (
                settings
                .OTP_EXPIRE_SECONDS
            ),

            "resend_in": (
                settings
                .OTP_RESEND_SECONDS
            ),
        }
        


    # async def reset_password(
    # self,
    # raw_token: str,
    # new_password: str,
    # ) -> None:

    #     token_hash_value = hash_token(
    #         raw_token
    #     )

    #     token_record = (
    #         await self.auth_tokens
    #         .get_password_reset_token(
    #             token_hash_value
    #         )
    #     )

    #     if not token_record:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Invalid or expired reset token",
    #         )

    #     if token_record.used_at is not None:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Reset token has already been used",
    #         )

    #     now = datetime.now(
    #         timezone.utc
    #     )

    #     if token_record.expires_at <= now:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Reset token has expired",
    #         )

    #     user = await self.users.get_by_id(
    #         token_record.user_id
    #     )

    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Invalid reset token",
    #         )

    #     user.password_hash = hash_password(
    #         new_password
    #     )

    #     token_record.used_at = now

    #     # Log out every existing session
    #     await self.refresh_tokens.revoke_all_for_user(
    #         user.id
    #     )

    #     await self.db.commit()
        
        


    async def reset_password(
        self,
        raw_token: str,
        new_password: str,
    ) -> dict:

        token_hash_value = hash_token(
            raw_token
        )

        token_record = (
            await self.auth_tokens
            .get_password_reset_token(
                token_hash_value
            )
        )

        if not token_record:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid or expired reset token"
                ),
            )

        if token_record.used_at is not None:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Reset token has already been used"
                ),
            )

        now = datetime.now(
            timezone.utc
        )

        if token_record.expires_at <= now:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail="Reset token has expired",
            )

        user = await self.users.get_by_id(
            token_record.user_id
        )

        if (
            not user
            or not user.is_active
        ):

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail="Invalid reset token",
            )

        # =========================================================
        # OPTIONAL SAFETY:
        # Do not allow resetting to existing password.
        # =========================================================

        if verify_password(
            new_password,
            user.password_hash,
        ):

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "New password must be "
                    "different from your "
                    "current password"
                ),
            )

        # =========================================================
        # UPDATE PASSWORD
        # =========================================================

        user.password_hash = hash_password(
            new_password
        )

        user.is_verified = True

        token_record.used_at = now

        # =========================================================
        # REVOKE ALL OLD LOGIN SESSIONS
        # =========================================================

        await self.refresh_tokens \
            .revoke_all_for_user(
                user.id
            )

        # =========================================================
        # CREATE BRAND NEW SESSION
        #
        # IMPORTANT:
        # This must happen AFTER revoking old tokens.
        # =========================================================

        auth_data = (
            await self._create_auth_session(
                user
            )
        )

        await self.db.commit()

        await self.db.refresh(
            user
        )

        return {
            **auth_data,
            "user": user,
        }
        
    
    
    
    
    async def send_verification(
    self,
    user: User,
    ) -> None:

        if not user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email address associated with this account",
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified",
            )

        await self.auth_tokens.invalidate_email_tokens(
            user.id
        )

        raw_token = create_secure_token()

        verification = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(
                raw_token
            ),
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(
                    hours=(
                        settings
                        .EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
                    )
                )
            ),
        )

        self.db.add(
            verification
        )

        await self.db.commit()

        await EmailService.send_verification_email(
            recipient=user.email,
            token=raw_token,
        )
        
    
    
    async def verify_email(
    self,
    raw_token: str,
    ) -> User:

        token_hash_value = hash_token(
            raw_token
        )

        token_record = (
            await self.auth_tokens
            .get_email_verification_token(
                token_hash_value
            )
        )

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )

        if token_record.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token already used",
            )

        now = datetime.now(
            timezone.utc
        )

        if token_record.expires_at <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token expired",
            )

        user = await self.users.get_by_id(
            token_record.user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )

        user.is_verified = True

        token_record.used_at = now

        await self.db.commit()

        await self.db.refresh(user)

        return user






    async def _create_auth_session(
        self,
        user: User,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        # =========================================================
        # ACCESS TOKEN
        # =========================================================

        access_token = (
            create_access_token(
                user_id=user.id,
                role=user.role,
            )
        )

        # =========================================================
        # REFRESH TOKEN
        # =========================================================

        refresh_token = (
            create_refresh_token()
        )

        refresh_record = RefreshToken(
            user_id=user.id,

            token_hash=hash_token(
                refresh_token
            ),

            expires_at=(
                now
                + timedelta(
                    days=(
                        settings
                        .REFRESH_TOKEN_EXPIRE_DAYS
                    )
                )
            ),
        )

        self.db.add(
            refresh_record
        )

        user.last_login_at = now

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": (
                settings
                .ACCESS_TOKEN_EXPIRE_MINUTES
                * 60
            ),
        }
        
        
        


    async def verify_registration_otp(
        self,
        *,
        challenge_id: str,
        otp: str,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        # =========================================================
        # LOAD + LOCK OTP SESSION
        # =========================================================

        otp_session = (
            await self.phone_otps
            .get_by_challenge_id_for_update(
                challenge_id.strip()
            )
        )

        if not otp_session:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid or expired "
                    "verification code"
                ),
            )

        # =========================================================
        # PURPOSE
        # =========================================================

        if (
            otp_session.purpose
            != "REGISTRATION"
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid verification "
                    "request"
                ),
            )

        # =========================================================
        # ALREADY CONSUMED
        # =========================================================

        if otp_session.consumed_at is not None:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Verification code is "
                    "no longer valid"
                ),
            )

        # =========================================================
        # EXPIRED
        # =========================================================

        if otp_session.expires_at <= now:

            otp_session.consumed_at = now

            await self.db.commit()

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Verification code expired. "
                    "Please request a new code."
                ),
            )

        # =========================================================
        # ATTEMPT LIMIT
        # =========================================================

        if (
            otp_session.attempts
            >= settings.OTP_MAX_ATTEMPTS
        ):

            otp_session.consumed_at = now

            await self.db.commit()

            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many incorrect attempts. "
                    "Please request a new code."
                ),
            )

        # =========================================================
        # VERIFY OTP
        # =========================================================

        otp_valid = verify_otp_hash(
            challenge_id=(
                otp_session.challenge_id
            ),
            otp=otp.strip(),
            expected_hash=(
                otp_session.otp_hash
            ),
        )

        if not otp_valid:

            otp_session.attempts += 1

            attempts_left = max(
                0,
                settings.OTP_MAX_ATTEMPTS
                - otp_session.attempts,
            )

            # Final failed attempt permanently consumes this OTP.
            if attempts_left == 0:
                otp_session.consumed_at = now

            await self.db.commit()

            if attempts_left == 0:
                raise HTTPException(
                    status_code=(
                        status.HTTP_429_TOO_MANY_REQUESTS
                    ),
                    detail=(
                        "Too many incorrect attempts. "
                        "Please request a new code."
                    ),
                )

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    f"Incorrect verification code. "
                    f"{attempts_left} "
                    f"attempts remaining."
                ),
            )

        # =========================================================
        # LOAD USER
        # =========================================================

        user = await self.users.get_by_id(
            otp_session.user_id
        )

        if not user:
            await self.db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail="Invalid verification request",
            )

        if not user.is_active:
            await self.db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail="Account is disabled",
            )

        # =========================================================
        # VERIFY USER PHONE
        # =========================================================

        user.is_verified = True

        otp_session.verified_at = now
        otp_session.consumed_at = now

        # Invalidate any other registration OTPs for this account.
        await self.phone_otps.invalidate_active(
            user_id=user.id,
            purpose="REGISTRATION",
            exclude_id=otp_session.id,
        )

        # =========================================================
        # CREATE LOGIN SESSION
        # =========================================================

        auth_data = (
            await self._create_auth_session(
                user
            )
        )

        # =========================================================
        # ONE ATOMIC COMMIT
        # =========================================================

        await self.db.commit()

        await self.db.refresh(
            user
        )

        return {
            **auth_data,
            "user": user,
        }
        
        
        
            

    async def resend_registration_otp(
        self,
        *,
        challenge_id: str,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        # =========================================================
        # LOAD CURRENT CHALLENGE
        # =========================================================

        old_session = (
            await self.phone_otps
            .get_by_challenge_id_for_update(
                challenge_id.strip()
            )
        )

        if not old_session:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid verification "
                    "request"
                ),
            )

        if (
            old_session.purpose
            != "REGISTRATION"
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid verification "
                    "request"
                ),
            )

        # =========================================================
        # USER
        # =========================================================

        user = await self.users.get_by_id(
            old_session.user_id
        )

        if not user:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail="Invalid verification request",
            )

        if user.is_verified:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Phone number is already verified"
                ),
            )

        if not user.is_active:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail="Account is disabled",
            )

        # =========================================================
        # 30 SECOND COOLDOWN
        # =========================================================

        if (
            old_session.resend_available_at
            > now
        ):

            seconds_left = max(
                1,
                int(
                    (
                        old_session
                        .resend_available_at
                        - now
                    ).total_seconds()
                ),
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    f"Please wait "
                    f"{seconds_left} seconds "
                    f"before requesting "
                    f"another OTP."
                ),
            )

        # =========================================================
        # MAX 3 SENDS / 5 MINUTES
        # =========================================================

        five_minutes_ago = (
            now
            - timedelta(
                minutes=5
            )
        )

        recent_send_count = (
            await self.phone_otps
            .count_recent_sends(
                user_id=user.id,
                purpose="REGISTRATION",
                since=five_minutes_ago,
            )
        )

        if recent_send_count >= 3:
            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many OTP requests. "
                    "Please wait a few minutes "
                    "and try again."
                ),
            )

        # =========================================================
        # GENERATE NEW OTP
        # =========================================================

        otp = generate_otp()

        new_challenge_id = (
            generate_challenge_id()
        )

        idempotency_key = (
            generate_idempotency_key()
        )

        otp_hash_value = hash_otp(
            challenge_id=(
                new_challenge_id
            ),
            otp=otp,
        )

        expires_at = (
            now
            + timedelta(
                seconds=(
                    settings
                    .OTP_EXPIRE_SECONDS
                )
            )
        )

        resend_available_at = (
            now
            + timedelta(
                seconds=(
                    settings
                    .OTP_RESEND_SECONDS
                )
            )
        )

        # =========================================================
        # CREATE NEW SESSION
        # =========================================================

        new_session = PhoneOtpSession(
            challenge_id=(
                new_challenge_id
            ),
            user_id=user.id,
            purpose="REGISTRATION",
            phone=user.phone,
            otp_hash=otp_hash_value,
            provider_request_id=None,
            idempotency_key=(
                idempotency_key
            ),
            attempts=0,
            expires_at=expires_at,
            resend_available_at=(
                resend_available_at
            ),
        )

        try:

            await self.phone_otps.create(
                new_session
            )

            # =====================================================
            # SEND NEW SMS
            # =====================================================

            provider_request_id = (
                await StartMessagingService
                .send_otp(
                    phone=user.phone,
                    otp=otp,
                    idempotency_key=(
                        idempotency_key
                    ),
                )
            )

            new_session.provider_request_id = (
                provider_request_id
            )

            # Only invalidate the old OTP after the
            # new SMS has successfully been accepted.
            old_session.consumed_at = now

            await self.phone_otps.invalidate_active(
                user_id=user.id,
                purpose="REGISTRATION",
                exclude_id=new_session.id,
            )

            await self.db.commit()

        except StartMessagingError as exc:

            await self.db.rollback()

            logger.exception(
                "Registration OTP resend failed"
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "Unable to send verification "
                    "code right now. Please try again."
                ),
            ) from exc

        except HTTPException:

            await self.db.rollback()

            raise

        except Exception:

            await self.db.rollback()

            logger.exception(
                "Registration OTP resend failed"
            )

            raise

        return {
            "verification_required": True,
            "challenge_id": (
                new_challenge_id
            ),
            "phone_masked": (
                self._mask_phone(
                    user.phone
                )
            ),
            "expires_in": (
                settings
                .OTP_EXPIRE_SECONDS
            ),
            "resend_in": (
                settings
                .OTP_RESEND_SECONDS
            ),
        }
        
        




    def _otp_challenge_response(
        self,
        *,
        session: PhoneOtpSession,
        now: datetime | None = None,
    ) -> dict:

        now = (
            now
            or datetime.now(
                timezone.utc
            )
        )

        expires_in = max(
            0,
            int(
                (
                    session.expires_at
                    - now
                ).total_seconds()
            ),
        )

        resend_in = max(
            0,
            int(
                (
                    session
                    .resend_available_at
                    - now
                ).total_seconds()
            ),
        )

        return {
            "verification_required": True,
            "challenge_id": (
                session.challenge_id
            ),
            "phone_masked": (
                self._mask_phone(
                    session.phone
                )
            ),
            "expires_in": expires_in,
            "resend_in": resend_in,
        }
        
    



    async def _start_login_verification(
        self,
        user: User,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        # =========================================================
        # REUSE CURRENT VALID CHALLENGE
        # =========================================================
        #
        # Prevent Login button presses from repeatedly sending SMS.
        # =========================================================

        existing = (
            await self.phone_otps
            .get_latest_active(
                user_id=user.id,
                purpose=(
                    "LOGIN_VERIFICATION"
                ),
            )
        )

        if existing:

            if (
                existing.expires_at > now
                and
                existing.attempts
                < settings.OTP_MAX_ATTEMPTS
            ):
                return (
                    self._otp_challenge_response(
                        session=existing,
                        now=now,
                    )
                )

        # =========================================================
        # 3 SENDS / 5 MINUTES
        # =========================================================

        recent_send_count = (
            await self.phone_otps
            .count_recent_sends(
                user_id=user.id,
                purpose=(
                    "LOGIN_VERIFICATION"
                ),
                since=(
                    now
                    - timedelta(
                        minutes=5
                    )
                ),
            )
        )

        if recent_send_count >= 3:
            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many verification "
                    "requests. Please wait a "
                    "few minutes and try again."
                ),
            )

        # =========================================================
        # CREATE OTP
        # =========================================================

        otp = generate_otp()

        challenge_id = (
            generate_challenge_id()
        )

        idempotency_key = (
            generate_idempotency_key()
        )

        otp_hash_value = hash_otp(
            challenge_id=challenge_id,
            otp=otp,
        )

        session = PhoneOtpSession(
            challenge_id=challenge_id,
            user_id=user.id,
            purpose=(
                "LOGIN_VERIFICATION"
            ),
            phone=user.phone,
            otp_hash=otp_hash_value,
            provider_request_id=None,
            idempotency_key=(
                idempotency_key
            ),
            attempts=0,

            expires_at=(
                now
                + timedelta(
                    seconds=(
                        settings
                        .OTP_EXPIRE_SECONDS
                    )
                )
            ),

            resend_available_at=(
                now
                + timedelta(
                    seconds=(
                        settings
                        .OTP_RESEND_SECONDS
                    )
                )
            ),
        )

        try:

            await self.phone_otps.create(
                session
            )

            provider_request_id = (
                await StartMessagingService
                .send_otp(
                    phone=user.phone,
                    otp=otp,
                    idempotency_key=(
                        idempotency_key
                    ),
                )
            )

            session.provider_request_id = (
                provider_request_id
            )

            # New SMS succeeded.
            # Old LOGIN_VERIFICATION codes can now die.
            await self.phone_otps.invalidate_active(
                user_id=user.id,
                purpose=(
                    "LOGIN_VERIFICATION"
                ),
                exclude_id=session.id,
            )

            await self.db.commit()

            await self.db.refresh(
                session
            )

        except StartMessagingError as exc:

            await self.db.rollback()

            logger.exception(
                "Login verification OTP "
                "delivery failed"
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "Unable to send verification "
                    "code right now. Please try again."
                ),
            ) from exc

        except Exception:

            await self.db.rollback()

            logger.exception(
                "Login verification failed"
            )

            raise

        return (
            self._otp_challenge_response(
                session=session,
                now=now,
            )
        )
    
    
        
    async def resend_login_otp(
        self,
        *,
        challenge_id: str,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        old_session = (
            await self.phone_otps
            .get_by_challenge_id_for_update(
                challenge_id.strip()
            )
        )

        if (
            not old_session
            or old_session.purpose
            != "LOGIN_VERIFICATION"
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid verification "
                    "request"
                ),
            )

        user = await self.users.get_by_id(
            old_session.user_id
        )

        if not user:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail="Invalid verification request",
            )

        if user.is_verified:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Phone number is already verified"
                ),
            )

        if old_session.resend_available_at > now:

            seconds_left = max(
                1,
                int(
                    (
                        old_session
                        .resend_available_at
                        - now
                    ).total_seconds()
                ),
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    f"Please wait "
                    f"{seconds_left} seconds "
                    f"before requesting "
                    f"another OTP."
                ),
            )

        recent_count = (
            await self.phone_otps
            .count_recent_sends(
                user_id=user.id,
                purpose=(
                    "LOGIN_VERIFICATION"
                ),
                since=(
                    now
                    - timedelta(
                        minutes=5
                    )
                ),
            )
        )

        if recent_count >= 3:
            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many OTP requests. "
                    "Please wait a few minutes "
                    "and try again."
                ),
            )

        otp = generate_otp()

        new_challenge_id = (
            generate_challenge_id()
        )

        idempotency_key = (
            generate_idempotency_key()
        )

        session = PhoneOtpSession(
            challenge_id=(
                new_challenge_id
            ),
            user_id=user.id,
            purpose=(
                "LOGIN_VERIFICATION"
            ),
            phone=user.phone,

            otp_hash=hash_otp(
                challenge_id=(
                    new_challenge_id
                ),
                otp=otp,
            ),

            provider_request_id=None,

            idempotency_key=(
                idempotency_key
            ),

            attempts=0,

            expires_at=(
                now
                + timedelta(
                    seconds=(
                        settings
                        .OTP_EXPIRE_SECONDS
                    )
                )
            ),

            resend_available_at=(
                now
                + timedelta(
                    seconds=(
                        settings
                        .OTP_RESEND_SECONDS
                    )
                )
            ),
        )

        try:

            await self.phone_otps.create(
                session
            )

            provider_request_id = (
                await StartMessagingService
                .send_otp(
                    phone=user.phone,
                    otp=otp,
                    idempotency_key=(
                        idempotency_key
                    ),
                )
            )

            session.provider_request_id = (
                provider_request_id
            )

            old_session.consumed_at = now

            await self.phone_otps.invalidate_active(
                user_id=user.id,
                purpose=(
                    "LOGIN_VERIFICATION"
                ),
                exclude_id=session.id,
            )

            await self.db.commit()

        except StartMessagingError as exc:

            await self.db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "Unable to send verification "
                    "code right now. Please try again."
                ),
            ) from exc

        return (
            self._otp_challenge_response(
                session=session,
                now=now,
            )
        )



    def _fake_password_reset_response(
        self,
    ) -> dict:

        return {
            "verification_required": True,
            "challenge_id": (
                generate_challenge_id()
            ),
            "expires_in": (
                settings.OTP_EXPIRE_SECONDS
            ),
            "resend_in": (
                settings.OTP_RESEND_SECONDS
            ),
        }
        



    async def verify_password_reset_otp(
        self,
        *,
        challenge_id: str,
        otp: str,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        session = (
            await self.phone_otps
            .get_by_challenge_id_for_update(
                challenge_id.strip()
            )
        )

        if not session:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid or expired "
                    "verification code"
                ),
            )

        # =========================================================
        # PURPOSE
        # =========================================================

        if (
            session.purpose
            != "PASSWORD_RESET"
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Invalid password reset request"
                ),
            )

        # =========================================================
        # CONSUMED
        # =========================================================

        if session.consumed_at is not None:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Verification code is "
                    "no longer valid"
                ),
            )

        # =========================================================
        # EXPIRED
        # =========================================================

        if session.expires_at <= now:

            session.consumed_at = now

            await self.db.commit()

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Verification code expired. "
                    "Please request a new code."
                ),
            )

        # =========================================================
        # ATTEMPT LIMIT
        # =========================================================

        if (
            session.attempts
            >= settings.OTP_MAX_ATTEMPTS
        ):

            session.consumed_at = now

            await self.db.commit()

            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many incorrect attempts. "
                    "Please request a new code."
                ),
            )

        # =========================================================
        # VERIFY OTP
        # =========================================================

        valid = verify_otp_hash(
            challenge_id=(
                session.challenge_id
            ),
            otp=otp.strip(),
            expected_hash=(
                session.otp_hash
            ),
        )

        if not valid:

            session.attempts += 1

            attempts_left = max(
                0,
                settings.OTP_MAX_ATTEMPTS
                - session.attempts,
            )

            if attempts_left == 0:
                session.consumed_at = now

            await self.db.commit()

            if attempts_left == 0:

                raise HTTPException(
                    status_code=(
                        status
                        .HTTP_429_TOO_MANY_REQUESTS
                    ),
                    detail=(
                        "Too many incorrect attempts. "
                        "Please request a new code."
                    ),
                )

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    f"Incorrect verification code. "
                    f"{attempts_left} attempts remaining."
                ),
            )

        # =========================================================
        # USER
        # =========================================================

        user = await self.users.get_by_id(
            session.user_id
        )

        if (
            not user
            or not user.is_active
        ):

            await self.db.rollback()

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail="Invalid password reset request",
            )

        # =========================================================
        # PHONE OWNERSHIP HAS BEEN PROVEN
        # =========================================================

        user.is_verified = True

        session.verified_at = now
        session.consumed_at = now

        await self.phone_otps.invalidate_active(
            user_id=user.id,
            purpose="PASSWORD_RESET",
            exclude_id=session.id,
        )

        # =========================================================
        # INVALIDATE PREVIOUS RESET GRANTS
        # =========================================================

        await self.auth_tokens \
            .invalidate_password_reset_tokens(
                user.id
            )

        # =========================================================
        # CREATE SHORT-LIVED RESET GRANT
        # =========================================================

        raw_reset_token = (
            create_secure_token()
        )

        reset_record = (
            PasswordResetToken(
                user_id=user.id,

                token_hash=hash_token(
                    raw_reset_token
                ),

                expires_at=(
                    now
                    + timedelta(
                        minutes=10
                    )
                ),
            )
        )

        self.db.add(
            reset_record
        )

        await self.db.commit()

        return {
            "reset_token": (
                raw_reset_token
            ),

            "expires_in": 600,
        }
        
        


    async def resend_password_reset_otp(
        self,
        *,
        challenge_id: str,
    ) -> dict:

        now = datetime.now(
            timezone.utc
        )

        old_session = (
            await self.phone_otps
            .get_by_challenge_id_for_update(
                challenge_id.strip()
            )
        )

        # =========================================================
        # FAKE / INVALID CHALLENGE
        #
        # Still return generic response.
        # =========================================================

        if (
            not old_session
            or old_session.purpose
            != "PASSWORD_RESET"
        ):
            return (
                self
                ._fake_password_reset_response()
            )

        user = await self.users.get_by_id(
            old_session.user_id
        )

        if (
            not user
            or not user.is_active
        ):
            return (
                self
                ._fake_password_reset_response()
            )

        # =========================================================
        # COOLDOWN
        # =========================================================

        if (
            old_session
            .resend_available_at
            > now
        ):

            seconds_left = max(
                1,
                int(
                    (
                        old_session
                        .resend_available_at
                        - now
                    ).total_seconds()
                ),
            )

            raise HTTPException(
                status_code=(
                    status
                    .HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    f"Please wait "
                    f"{seconds_left} seconds "
                    f"before requesting "
                    f"another OTP."
                ),
            )

        # =========================================================
        # 3 SENDS / 5 MINUTES
        # =========================================================

        recent_count = (
            await self.phone_otps
            .count_recent_sends(
                user_id=user.id,
                purpose="PASSWORD_RESET",
                since=(
                    now
                    - timedelta(
                        minutes=5
                    )
                ),
            )
        )

        if recent_count >= 3:

            raise HTTPException(
                status_code=(
                    status
                    .HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many OTP requests. "
                    "Please wait a few minutes "
                    "and try again."
                ),
            )

        # =========================================================
        # NEW OTP SESSION
        # =========================================================

        otp = generate_otp()

        new_challenge_id = (
            generate_challenge_id()
        )

        idempotency_key = (
            generate_idempotency_key()
        )

        new_session = PhoneOtpSession(
            challenge_id=(
                new_challenge_id
            ),

            user_id=user.id,

            purpose="PASSWORD_RESET",

            phone=user.phone,

            otp_hash=hash_otp(
                challenge_id=(
                    new_challenge_id
                ),
                otp=otp,
            ),

            provider_request_id=None,

            idempotency_key=(
                idempotency_key
            ),

            attempts=0,

            expires_at=(
                now
                + timedelta(
                    seconds=(
                        settings
                        .OTP_EXPIRE_SECONDS
                    )
                )
            ),

            resend_available_at=(
                now
                + timedelta(
                    seconds=(
                        settings
                        .OTP_RESEND_SECONDS
                    )
                )
            ),
        )

        try:

            await self.phone_otps.create(
                new_session
            )

            provider_request_id = (
                await StartMessagingService
                .send_otp(
                    phone=user.phone,
                    otp=otp,
                    idempotency_key=(
                        idempotency_key
                    ),
                )
            )

            new_session.provider_request_id = (
                provider_request_id
            )

            old_session.consumed_at = now

            await self.phone_otps.invalidate_active(
                user_id=user.id,
                purpose="PASSWORD_RESET",
                exclude_id=new_session.id,
            )

            await self.db.commit()

        except StartMessagingError as exc:

            await self.db.rollback()

            logger.exception(
                "Password reset OTP resend failed"
            )

            raise HTTPException(
                status_code=(
                    status
                    .HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "Unable to send verification "
                    "code right now. Please try again."
                ),
            ) from exc

        return {
            "verification_required": True,

            "challenge_id": (
                new_challenge_id
            ),

            "expires_in": (
                settings
                .OTP_EXPIRE_SECONDS
            ),

            "resend_in": (
                settings
                .OTP_RESEND_SECONDS
            ),
        }
        
        
        
   
   
    
      
    
    @staticmethod
    def _mask_phone(
        phone: str,
    ) -> str:

        if len(phone) <= 4:
            return phone

        return (
            "*" * (
                len(phone) - 4
            )
            + phone[-4:]
        )
        
        
        
    async def delivery_login(
        self,
        identifier: str,
        password: str,
    ) -> dict:

        identifier = identifier.strip()

        # =========================================================
        # NORMALIZE IDENTIFIER
        # =========================================================

        if "@" in identifier:
            identifier = (
                identifier
                .lower()
                .strip()
            )

            condition = (
                User.email == identifier
            )

        else:
            try:
                identifier = (
                    normalize_indian_phone(
                        identifier
                    )
                )

            except HTTPException:
                raise HTTPException(
                    status_code=(
                        status.HTTP_401_UNAUTHORIZED
                    ),
                    detail="Invalid credentials",
                )

            condition = (
                User.phone == identifier
            )

        # =========================================================
        # LOAD USER + DELIVERY PROFILE
        # =========================================================

        result = await self.db.execute(
            select(User)
            .options(
                selectinload(
                    User.delivery_profile
                )
            )
            .where(condition)
        )

        user = result.scalar_one_or_none()

        # =========================================================
        # USER EXISTS
        # =========================================================

        if not user:
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Invalid credentials",
            )

        # =========================================================
        # PASSWORD
        # =========================================================

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Invalid credentials",
            )

        # =========================================================
        # ROLE
        # =========================================================

        if user.role != "DELIVERY_PARTNER":
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Delivery partner access required"
                ),
            )

        # =========================================================
        # ACTIVE ACCOUNT
        # =========================================================

        if not user.is_active:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Delivery account is disabled"
                ),
            )

        # =========================================================
        # VERIFIED ACCOUNT
        # =========================================================

        if not user.is_verified:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Delivery account is not verified"
                ),
            )

        # =========================================================
        # DELIVERY PROFILE
        # =========================================================

        profile = user.delivery_profile

        if profile is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Delivery partner profile not found"
                ),
            )

        # =========================================================
        # ADMIN APPROVAL
        # =========================================================

        if not profile.is_approved:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Delivery account is awaiting "
                    "admin approval"
                ),
            )

        # =========================================================
        # CREATE NORMAL GRAMAGO AUTH SESSION
        # =========================================================

        auth_data = (
            await self._create_auth_session(
                user
            )
        )

        await self.db.commit()

        await self.db.refresh(
            user
        )

        # Reload relationship after commit/refresh.
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(
                    User.delivery_profile
                )
            )
            .where(
                User.id == user.id
            )
        )

        user = result.scalar_one()

        return {
            "authenticated": True,
            "verification_required": False,
            **auth_data,
            "user": user,
        }
        
        
        

