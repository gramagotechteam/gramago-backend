from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CommerceSetting(Base):
    __tablename__ = "commerce_settings"

    # ---------------------------------------------------------
    # SINGLE GLOBAL SETTINGS ROW
    #
    # For V1 we intentionally keep exactly one row:
    # id = 1
    # ---------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
        default=1,
    )

    # ---------------------------------------------------------
    # MINIMUM CART SUBTOTAL REQUIRED TO PLACE AN ORDER
    # ---------------------------------------------------------

    minimum_order_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )

    # ---------------------------------------------------------
    # DELIVERY FEE
    #
    # 0.00 means FREE DELIVERY.
    # We do NOT store a separate is_free_delivery flag.
    # ---------------------------------------------------------

    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("16.00"),
        server_default="16.00",
    )

    # ---------------------------------------------------------
    # ADMIN WHO LAST CHANGED THE SETTINGS
    # ---------------------------------------------------------

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "id = 1",
            name="chk_commerce_settings_singleton",
        ),
        CheckConstraint(
            "minimum_order_amount >= 0",
            name="chk_commerce_settings_minimum_non_negative",
        ),
        CheckConstraint(
            "delivery_fee >= 0",
            name="chk_commerce_settings_delivery_fee_non_negative",
        ),
    )

    @property
    def is_free_delivery(self) -> bool:
        return self.delivery_fee == Decimal("0.00")