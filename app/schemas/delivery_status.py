from pydantic import BaseModel, Field


class DeliveryOnlineStatusUpdate(BaseModel):
    is_online: bool


class DeliveryAvailabilityUpdate(BaseModel):
    is_available: bool


class DeliveryLocationUpdate(BaseModel):
    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )


class DeliveryStatusResponse(BaseModel):
    is_online: bool
    is_available: bool

    current_latitude: float | None
    current_longitude: float | None

    last_location_at: str | None = None