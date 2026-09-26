from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
)


class CartAddItemRequest(BaseModel):

    product_id: int

    quantity: Decimal = Field(
        gt=0
    )


class CartUpdateItemRequest(BaseModel):

    quantity: Decimal = Field(
        gt=0
    )