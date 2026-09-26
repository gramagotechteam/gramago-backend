# from datetime import datetime

# from pydantic import BaseModel, ConfigDict, EmailStr, Field


# class UserRegister(BaseModel):
#     full_name: str = Field(
#         min_length=2,
#         max_length=120,
#     )

#     phone: str = Field(
#         min_length=10,
#         max_length=20,
#     )

#     email: EmailStr | None = None

#     password: str = Field(
#         min_length=8,
#         max_length=128,
#     )


# class UserResponse(BaseModel):
#     id: int
#     full_name: str
#     email: str | None
#     phone: str
#     role: str
#     is_active: bool
#     is_verified: bool
#     created_at: datetime

#     model_config = ConfigDict(
#         from_attributes=True
#     )


# class UserUpdate(BaseModel):
#     full_name: str | None = Field(
#         default=None,
#         min_length=2,
#         max_length=120,
#     )

#     email: EmailStr | None = None


from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class UserRegister(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=120,
    )

    phone: str = Field(
        min_length=10,
        max_length=20,
    )

    email: EmailStr | None = None

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str | None
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    email: EmailStr | None = None