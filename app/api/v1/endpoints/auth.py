
import logging

logger = logging.getLogger(__name__)




from app.core.rate_limit import RateLimiter

login_limiter = RateLimiter(
    limit=5,
    window_seconds=60,
)

forgot_password_limiter = RateLimiter(
    limit=3,
    window_seconds=300,
)

verification_limiter = RateLimiter(
    limit=3,
    window_seconds=300,
)

refresh_limiter = RateLimiter(
    limit=20,
    window_seconds=60,
)


register_limiter = RateLimiter(
    limit=3,
    window_seconds=300,
)



otp_verify_limiter = RateLimiter(
    limit=10,
    window_seconds=60,
)

otp_resend_limiter = RateLimiter(
    limit=5,
    window_seconds=300,
)

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
# from app.schemas.auth import LoginRequest


from app.schemas.user import (
    UserRegister,
    UserResponse,
)

# from app.schemas.auth import (
#     ChangePasswordRequest,
#     LoginRequest,
#     LogoutRequest,
#     RefreshTokenRequest,
# )

from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    ResendLoginOtpRequest,
    ResendPasswordResetOtpRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    VerifyLoginOtpRequest,
    VerifyPasswordResetOtpRequest,
)
from app.services.auth_service import AuthService

from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    VerifyRegistrationOtpRequest,
    ResendRegistrationOtpRequest,
)



router = APIRouter()


# @router.post(
#     "/register",
#     status_code=status.HTTP_201_CREATED,
# )
# async def register(
#     data: UserRegister,
#     db: AsyncSession = Depends(get_db),
# ):

#     service = AuthService(db)

#     user = await service.register(data)
    
#     if user.email:

#         try:
#             await service.send_verification(
#                 user
#             )

#         except Exception:
#             logger.exception(
#                 "Registration verification email failed"
#             )

#     return {
#         "success": True,
#         "message": "Registration successful",
#         "data": UserResponse.model_validate(
#             user
#         ),
#     }




@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,

    _: None = Depends(
        register_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    service = AuthService(db)

    result = await service.register(
        data
    )

    return {
        "success": True,
        "message": (
            "Account created. "
            "Enter the OTP sent to "
            "your mobile number."
        ),
        "data": result,
    }
    









@router.post(
    "/verify-registration-otp"
)
async def verify_registration_otp(
    data: VerifyRegistrationOtpRequest,

    _: None = Depends(
        otp_verify_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service
        .verify_registration_otp(
            challenge_id=(
                data.challenge_id
            ),
            otp=data.otp,
        )
    )

    user = result.pop(
        "user"
    )

    return {
        "success": True,
        "message": (
            "Phone number verified "
            "successfully"
        ),
        "data": {
            **result,
            "user": (
                UserResponse
                .model_validate(
                    user
                )
            ),
        },
    }
    
    
    
    
    
    
    
    
@router.post(
    "/resend-registration-otp"
)
async def resend_registration_otp(
    data: ResendRegistrationOtpRequest,

    _: None = Depends(
        otp_resend_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service
        .resend_registration_otp(
            challenge_id=(
                data.challenge_id
            )
        )
    )

    return {
        "success": True,
        "message": (
            "A new verification code "
            "has been sent."
        ),
        "data": result,
    }
    
    
    





# @router.post("/refresh")
# async def refresh_token(
#     data: RefreshTokenRequest,
#     db: AsyncSession = Depends(get_db),
# ):

@router.post("/refresh")
async def refresh_token(
    data: RefreshTokenRequest,

    _: None = Depends(
        refresh_limiter
    ),

    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    result = await service.refresh(
        data.refresh_token
    )

    return {
        "success": True,
        "message": "Token refreshed successfully",
        "data": result,
    }
    

# @router.post("/login")
# async def login(
#     data: LoginRequest,
#     db: AsyncSession = Depends(get_db),
# ):







# @router.post("/login")
# async def login(
#     data: LoginRequest,
#     _: None = Depends(
#         login_limiter
#     ),
#     db: AsyncSession = Depends(get_db),
# ):
#     service = AuthService(db)

#     result = await service.login(
#         data.identifier,
#         data.password,
#     )

#     user = result.pop("user")

#     return {
#         "success": True,
#         "message": "Login successful",
#         "data": {
#             **result,
#             "user": UserResponse.model_validate(
#                 user
#             ),
#         },
#     }
    
    


@router.post("/login")
async def login(
    data: LoginRequest,

    _: None = Depends(
        login_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = await service.login(
        data.identifier,
        data.password,
    )

    # =========================================================
    # OTP REQUIRED
    # =========================================================

    if result.get(
        "verification_required"
    ):

        return {
            "success": True,
            "message": (
                "Phone verification required. "
                "Enter the OTP sent to your "
                "mobile number."
            ),
            "data": result,
        }

    # =========================================================
    # NORMAL LOGIN
    # =========================================================

    user = result.pop(
        "user"
    )

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            **result,

            "user": (
                UserResponse
                .model_validate(
                    user
                )
            ),
        },
    }





@router.post(
    "/verify-login-otp"
)
async def verify_login_otp(
    data: VerifyLoginOtpRequest,

    _: None = Depends(
        otp_verify_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service
        .verify_login_otp(
            challenge_id=(
                data.challenge_id
            ),
            otp=data.otp,
        )
    )

    user = result.pop(
        "user"
    )

    return {
        "success": True,
        "message": (
            "Phone verified and "
            "login successful"
        ),
        "data": {
            **result,

            "user": (
                UserResponse
                .model_validate(
                    user
                )
            ),
        },
    }
    
    
    
    


@router.post(
    "/resend-login-otp"
)
async def resend_login_otp(
    data: ResendLoginOtpRequest,

    _: None = Depends(
        otp_resend_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service
        .resend_login_otp(
            challenge_id=(
                data.challenge_id
            )
        )
    )

    return {
        "success": True,
        "message": (
            "A new verification code "
            "has been sent."
        ),
        "data": result,
    }
    
    
    
    
@router.post("/logout")
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    await service.logout(
        data.refresh_token
    )

    return {
        "success": True,
        "message": "Logout successful",
        "data": None,
    }
    
    


from app.dependencies.auth import get_current_user
from app.models.user import User



@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    await service.logout_all(
        current_user.id
    )

    return {
        "success": True,
        "message": "Logged out from all devices",
        "data": None,
    }
    
    




@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    await service.change_password(
        user=current_user,
        current_password=data.current_password,
        new_password=data.new_password,
    )

    return {
        "success": True,
        "message": "Password changed successfully. Please login again.",
        "data": None,
    }
    





# @router.post("/forgot-password")
# async def forgot_password(
#     data: ForgotPasswordRequest,
#     db: AsyncSession = Depends(get_db),
# ):

# @router.post("/forgot-password")
# async def forgot_password(
#     data: ForgotPasswordRequest,

#     _: None = Depends(
#         forgot_password_limiter
#     ),

#     db: AsyncSession = Depends(get_db),
# ):
#     service = AuthService(db)

#     await service.forgot_password(
#         data.email
#     )

#     return {
#         "success": True,
#         "message": (
#             "If an account exists with that email, "
#             "password reset instructions have been sent."
#         ),
#         "data": None,
#     }
    
    


@router.post(
    "/forgot-password"
)
async def forgot_password(
    data: ForgotPasswordRequest,

    _: None = Depends(
        forgot_password_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service
        .forgot_password(
            data.identifier
        )
    )

    return {
        "success": True,
        "message": (
            "If an eligible account exists, "
            "a verification code has been "
            "sent to the associated mobile number."
        ),
        "data": result,
    }


# @router.post("/reset-password")
# async def reset_password(
#     data: ResetPasswordRequest,
#     db: AsyncSession = Depends(get_db),
# ):

#     service = AuthService(db)

#     await service.reset_password(
#         raw_token=data.token,
#         new_password=data.new_password,
#     )

#     return {
#         "success": True,
#         "message": (
#             "Password reset successfully. "
#             "Please login again."
#         ),
#         "data": None,
#     }
    
    
    
    
    
    

@router.post(
    "/reset-password"
)
async def reset_password(
    data: ResetPasswordRequest,

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service
        .reset_password(
            raw_token=data.token,
            new_password=(
                data.new_password
            ),
        )
    )

    user = result.pop(
        "user"
    )

    return {
        "success": True,
        "message": (
            "Password reset successfully"
        ),
        "data": {
            **result,

            "user": (
                UserResponse
                .model_validate(
                    user
                )
            ),
        },
    }


# @router.post("/send-verification")
# async def send_verification(
#     current_user: User = Depends(
#         get_current_user
#     ),
#     db: AsyncSession = Depends(get_db),
# ):

@router.post("/send-verification")
async def send_verification(
    _: None = Depends(
        verification_limiter
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    await service.send_verification(
        current_user
    )

    return {
        "success": True,
        "message": "Verification email sent",
        "data": None,
    }
    




@router.post("/send-verification")
async def send_verification(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    service = AuthService(db)

    await service.send_verification(
        current_user
    )

    return {
        "success": True,
        "message": "Verification email sent",
        "data": None,
    }



@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):

    service = AuthService(db)

    user = await service.verify_email(
        data.token
    )

    return {
        "success": True,
        "message": "Email verified successfully",
        "data": UserResponse.model_validate(
            user
        ),
    }
    
    




@router.post(
    "/verify-password-reset-otp"
)
async def verify_password_reset_otp(
    data: VerifyPasswordResetOtpRequest,

    _: None = Depends(
        otp_verify_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service
        .verify_password_reset_otp(
            challenge_id=(
                data.challenge_id
            ),
            otp=data.otp,
        )
    )

    return {
        "success": True,
        "message": (
            "Verification successful. "
            "You can now reset your password."
        ),
        "data": result,
    }
    
    
    
    



@router.post(
    "/resend-password-reset-otp"
)
async def resend_password_reset_otp(
    data: ResendPasswordResetOtpRequest,

    _: None = Depends(
        otp_resend_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service
        .resend_password_reset_otp(
            challenge_id=(
                data.challenge_id
            )
        )
    )

    return {
        "success": True,
        "message": (
            "If the password reset request "
            "is valid, a new verification "
            "code has been sent."
        ),
        "data": result,
    }
    
    
    
    
    
