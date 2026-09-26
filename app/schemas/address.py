from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class AddressCreate(BaseModel):

    label: str | None = Field(
        default=None,
        max_length=50,
    )

    full_name: str = Field(
        min_length=2,
        max_length=120,
    )

    phone: str = Field(
        min_length=10,
        max_length=20,
    )

    house_no: str | None = None
    street: str | None = None

    village_town: str = Field(
        min_length=2,
        max_length=150,
    )

    mandal: str | None = None

    district: str = Field(
        min_length=2,
        max_length=150,
    )

    state: str = Field(
        min_length=2,
        max_length=150,
    )

    pincode: str = Field(
        min_length=4,
        max_length=10,
    )

    landmark: str | None = None

    latitude: Decimal | None = None
    longitude: Decimal | None = None

    is_default: bool = False


class AddressUpdate(BaseModel):

    label: str | None = None
    full_name: str | None = None
    phone: str | None = None

    house_no: str | None = None
    street: str | None = None

    village_town: str | None = None
    mandal: str | None = None
    district: str | None = None
    state: str | None = None

    pincode: str | None = None
    landmark: str | None = None

    latitude: Decimal | None = None
    longitude: Decimal | None = None

    is_default: bool | None = None


class AddressResponse(BaseModel):

    id: int

    label: str | None

    full_name: str
    phone: str

    house_no: str | None
    street: str | None

    village_town: str
    mandal: str | None
    district: str
    state: str

    pincode: str
    landmark: str | None

    latitude: Decimal | None
    longitude: Decimal | None

    is_default: bool
    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )