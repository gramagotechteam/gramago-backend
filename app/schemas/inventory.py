# from decimal import Decimal

# from pydantic import BaseModel, Field


# class StockAddRequest(BaseModel):

#     quantity: Decimal = Field(
#         gt=0
#     )

#     note: str | None = None


# class ReorderLevelRequest(BaseModel):

#     reorder_level: Decimal = Field(
#         ge=0
#     )




from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


class StockAddRequest(BaseModel):
    quantity: Decimal = Field(
        gt=0
    )

    note: str | None = None


class InventoryAdjustmentRequest(BaseModel):
    direction: Literal[
        "ADD",
        "REMOVE",
    ]

    quantity: Decimal = Field(
        gt=0
    )

    note: str


class DamagedStockRequest(BaseModel):
    quantity: Decimal = Field(
        gt=0
    )

    note: str | None = None


class ReorderLevelRequest(BaseModel):
    reorder_level: Decimal = Field(
        ge=0
    )