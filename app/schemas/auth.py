# from pydantic import BaseModel, Field


# class LoginRequest(BaseModel):
#     identifier: str
#     password: str


# class TokenPair(BaseModel):
#     access_token: str
#     refresh_token: str
#     token_type: str = "bearer"
#     expires_in: int


# class RefreshTokenRequest(BaseModel):
#     refresh_token: str


# class LogoutRequest(BaseModel):
#     refresh_token: str


# class ChangePasswordRequest(BaseModel):
#     current_password: str

#     new_password: str = Field(
#         min_length=8,
#         max_length=128,
#     )


# class ForgotPasswordRequest(BaseModel):
#     email: str


# class ResetPasswordRequest(BaseModel):
#     token: str

#     new_password: str = Field(
#         min_length=8,
#         max_length=128,
#     )


# class VerifyEmailRequest(BaseModel):
#     token: str




from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    identifier: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


# class ForgotPasswordRequest(BaseModel):
#     email: EmailStr

class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(
        min_length=3,
        max_length=255,
    )
    


class VerifyPasswordResetOtpRequest(
    BaseModel
):
    challenge_id: str = Field(
        min_length=32,
        max_length=64,
    )

    otp: str = Field(
        pattern=r"^\d{6}$",
    )


class ResendPasswordResetOtpRequest(
    BaseModel
):
    challenge_id: str = Field(
        min_length=32,
        max_length=64,
    )
    
    
class ResetPasswordRequest(BaseModel):
    token: str

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


class VerifyEmailRequest(BaseModel):
    token: str
    
    
    


class RegistrationOtpResponse(
    BaseModel
):
    verification_required: bool = True

    challenge_id: str

    phone_masked: str

    expires_in: int

    resend_in: int
    
    




class VerifyRegistrationOtpRequest(
    BaseModel
):
    challenge_id: str = Field(
        min_length=32,
        max_length=64,
    )

    otp: str = Field(
        pattern=r"^\d{6}$",
    )


class ResendRegistrationOtpRequest(
    BaseModel
):
    challenge_id: str = Field(
        min_length=32,
        max_length=64,
    )
    
    


class VerifyLoginOtpRequest(
    BaseModel
):
    challenge_id: str = Field(
        min_length=32,
        max_length=64,
    )

    otp: str = Field(
        pattern=r"^\d{6}$",
    )


class ResendLoginOtpRequest(
    BaseModel
):
    challenge_id: str = Field(
        min_length=32,
        max_length=64,
    )