# from datetime import datetime

# from pydantic import (
#     BaseModel,
#     ConfigDict,
# )


# class NotificationResponse(BaseModel):

#     id: int

#     notification_type: str

#     title: str
#     message: str

#     reference_type: str | None
#     reference_id: int | None

#     is_read: bool
#     read_at: datetime | None

#     created_at: datetime

#     model_config = ConfigDict(
#         from_attributes=True
#     )





from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class NotificationResponse(BaseModel):

    id: int

    notification_type: str

    category: str

    title: str

    message: str

    action: str

    reference_type: str | None = None

    reference_id: int | None = None

    image_url: str | None = None

    metadata_json: dict | None = None

    is_read: bool

    read_at: datetime | None = None

    created_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )


class NotificationPreferenceResponse(
    BaseModel
):

    transactional_enabled: bool

    product_updates_enabled: bool

    price_alerts_enabled: bool

    promotions_enabled: bool

    general_enabled: bool


    model_config = ConfigDict(
        from_attributes=True
    )


class NotificationPreferenceUpdate(
    BaseModel
):

    transactional_enabled: bool | None = None

    product_updates_enabled: bool | None = None

    price_alerts_enabled: bool | None = None

    promotions_enabled: bool | None = None

    general_enabled: bool | None = None