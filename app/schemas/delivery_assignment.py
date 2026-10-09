from datetime import datetime

from pydantic import BaseModel, Field


# ============================================================
# ADMIN ASSIGN ORDER
# ============================================================

class DeliveryOrderAssignRequest(BaseModel):
    order_id: int = Field(gt=0)
    delivery_partner_id: int = Field(gt=0)

    delivery_note: str | None = Field(
        default=None,
        max_length=1000,
    )


# ============================================================
# AVAILABLE PARTNER RESPONSE
# ============================================================

class AvailableDeliveryPartnerResponse(BaseModel):
    id: int

    full_name: str
    phone: str

    vehicle_type: str | None
    vehicle_number: str | None

    is_online: bool
    is_available: bool

    current_latitude: float | None = None
    current_longitude: float | None = None

    last_location_at: datetime | None = None


# ============================================================
# ASSIGNMENT RESPONSE
# ============================================================

class DeliveryAssignmentResponse(BaseModel):
    id: int

    order_id: int
    delivery_partner_id: int

    status: str

    assigned_at: datetime

    accepted_at: datetime | None = None
    rejected_at: datetime | None = None

    picked_up_at: datetime | None = None
    out_for_delivery_at: datetime | None = None
    delivered_at: datetime | None = None

    delivery_note: str | None = None