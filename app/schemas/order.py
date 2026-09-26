from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
)


class CheckoutRequest(BaseModel):

    address_id: int

    customer_note: str | None = Field(
        default=None,
        max_length=500,
    )


# class OrderStatusUpdate(BaseModel):

#     status: str

#     note: str | None = Field(
#         default=None,
#         max_length=500,
#     )


from typing import Literal

from pydantic import BaseModel, Field


class OrderStatusUpdate(BaseModel):

    status: Literal[
        "CONFIRMED",
        "PROCESSING",
        "PACKED",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "CANCELLED",
        "DELIVERY_FAILED",
    ]

    note: str | None = Field(
        default=None,
        max_length=500,
    )
    
    
from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
)


# class OrderItemResponse(BaseModel):

#     id: int
#     product_id: int | None

#     product_name: str

#     unit: str
#     unit_value: Decimal

#     quantity: Decimal

#     unit_price: Decimal
#     discount_amount: Decimal
#     line_total: Decimal

#     model_config = ConfigDict(
#         from_attributes=True
#     )


class OrderItemResponse(BaseModel):
    id: int

    product_id: int | None

    product_name: str

    image_url: str | None = None

    unit: str

    unit_value: Decimal

    quantity: Decimal

    unit_price: Decimal

    discount_amount: Decimal

    line_total: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )

class PaymentResponse(BaseModel):

    method: str
    status: str
    amount: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderHistoryResponse(BaseModel):

    from_status: str | None
    to_status: str

    note: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderListResponse(BaseModel):

    id: int
    order_number: str

    order_status: str
    payment_status: str

    total_amount: Decimal

    placed_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderDetailResponse(OrderListResponse):

    subtotal: Decimal
    delivery_fee: Decimal
    discount_amount: Decimal

    customer_note: str | None

    delivery_full_name: str
    delivery_phone: str

    delivery_house_no: str | None
    delivery_street: str | None

    delivery_village_town: str

    delivery_mandal: str | None
    delivery_district: str
    delivery_state: str

    delivery_pincode: str
    delivery_landmark: str | None

    items: list[
        OrderItemResponse
    ]

    payment: PaymentResponse | None

    status_history: list[
        OrderHistoryResponse
    ]
    
    



class AdminOrderListResponse(
    OrderListResponse
):

    user_id: int


class AdminOrderDetailResponse(
    OrderDetailResponse
):

    user_id: int