from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ============================================================
# ADMIN UPDATE
# ============================================================

class CommerceSettingsUpdate(
    BaseModel
):

    minimum_order_amount: (
        Decimal | None
    ) = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
    )

    delivery_fee: (
        Decimal | None
    ) = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
    )

    @model_validator(
        mode="after"
    )
    def validate_update(
        self,
    ):

        if (
            self.minimum_order_amount
            is None
            and
            self.delivery_fee
            is None
        ):
            raise ValueError(
                "At least one commerce "
                "setting must be provided"
            )

        return self


# ============================================================
# RESPONSE
# ============================================================

class CommerceSettingsResponse(
    BaseModel
):

    id: int

    minimum_order_amount: Decimal

    delivery_fee: Decimal

    is_free_delivery: bool

    updated_by: int | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )