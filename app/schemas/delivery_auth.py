from datetime import datetime

from pydantic import BaseModel, Field


class DeliveryLoginRequest(BaseModel):
    identifier: str = Field(
        min_length=3,
        max_length=255,
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class DeliveryRefreshRequest(BaseModel):
    refresh_token: str


class DeliveryLogoutRequest(BaseModel):
    refresh_token: str | None = None


class DeliveryPartnerMeResponse(BaseModel):
    id: int

    full_name: str
    email: str | None
    phone: str

    role: str

    is_active: bool
    is_verified: bool

    vehicle_type: str | None
    vehicle_number: str | None

    is_online: bool
    is_available: bool
    is_approved: bool

    created_at: datetime


class DeliveryLoginResponse(BaseModel):
    access_token: str
    refresh_token: str

    token_type: str = "bearer"

    user: DeliveryPartnerMeResponse