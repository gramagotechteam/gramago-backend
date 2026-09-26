from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "products.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # Product snapshot

    product_name: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
    )

    product_sku: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    unit: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    unit_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    line_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    order = relationship(
        "Order",
        back_populates="items",
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="chk_order_item_quantity",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="chk_order_item_price",
        ),
        CheckConstraint(
            "line_total >= 0",
            name="chk_order_item_total",
        ),
    )