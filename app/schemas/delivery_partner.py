# from datetime import datetime

# from pydantic import BaseModel, EmailStr, Field


# # ============================================================
# # CREATE
# # ============================================================

# class DeliveryPartnerCreate(BaseModel):
#     full_name: str = Field(
#         min_length=2,
#         max_length=120,
#     )

#     email: EmailStr | None = None

#     phone: str = Field(
#         min_length=10,
#         max_length=20,
#     )

#     password: str = Field(
#         min_length=8,
#         max_length=128,
#     )

#     vehicle_type: str | None = Field(
#         default=None,
#         max_length=50,
#     )

#     vehicle_number: str | None = Field(
#         default=None,
#         max_length=50,
#     )


# # ============================================================
# # UPDATE
# # ============================================================

# class DeliveryPartnerUpdate(BaseModel):
#     full_name: str | None = Field(
#         default=None,
#         min_length=2,
#         max_length=120,
#     )

#     email: EmailStr | None = None

#     phone: str | None = Field(
#         default=None,
#         min_length=10,
#         max_length=20,
#     )

#     vehicle_type: str | None = Field(
#         default=None,
#         max_length=50,
#     )

#     vehicle_number: str | None = Field(
#         default=None,
#         max_length=50,
#     )


# # ============================================================
# # APPROVAL
# # ============================================================

# class DeliveryPartnerApprovalUpdate(BaseModel):
#     is_approved: bool


# # ============================================================
# # ACTIVE STATUS
# # ============================================================

# class DeliveryPartnerActiveUpdate(BaseModel):
#     is_active: bool


# # ============================================================
# # RESPONSE
# # ============================================================

# class DeliveryPartnerResponse(BaseModel):
#     id: int

#     full_name: str
#     email: str | None
#     phone: str

#     role: str

#     is_active: bool
#     is_verified: bool

#     vehicle_type: str | None
#     vehicle_number: str | None

#     is_online: bool
#     is_available: bool
#     is_approved: bool

#     current_latitude: float | None = None
#     current_longitude: float | None = None

#     last_location_at: datetime | None = None

#     created_at: datetime

#     model_config = {
#         "from_attributes": True,
#     }



from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class DeliveryPartnerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr | None = None
    phone: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=8, max_length=128)

    vehicle_type: str | None = Field(default=None, max_length=50)
    vehicle_number: str | None = Field(default=None, max_length=50)


class DeliveryPartnerUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=20,
    )

    vehicle_type: str | None = Field(
        default=None,
        max_length=50,
    )

    vehicle_number: str | None = Field(
        default=None,
        max_length=50,
    )


class DeliveryPartnerApprovalUpdate(BaseModel):
    is_approved: bool


class DeliveryPartnerActiveUpdate(BaseModel):
    is_active: bool


class DeliveryPartnerResponse(BaseModel):
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

    current_latitude: float | None = None
    current_longitude: float | None = None

    last_location_at: datetime | None = None

    created_at: datetime