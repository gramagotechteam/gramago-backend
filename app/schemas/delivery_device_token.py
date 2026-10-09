from pydantic import BaseModel, Field


class DeliveryDeviceTokenCreate(
    BaseModel
):
    token: str = Field(
        min_length=20,
    )

    platform: str = "ANDROID"


class DeliveryDeviceTokenDelete(
    BaseModel
):
    token: str = Field(
        min_length=20,
    )