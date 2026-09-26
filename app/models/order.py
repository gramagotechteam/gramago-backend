from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    source_address_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "user_addresses.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    order_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="PLACED",
        index=True,
    )

    payment_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    customer_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Delivery address snapshot

    delivery_full_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    delivery_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    delivery_house_no: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    delivery_street: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    delivery_village_town: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    delivery_mandal: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    delivery_district: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    delivery_state: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    delivery_pincode: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    delivery_landmark: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    delivery_latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )

    delivery_longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )

    placed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    processing_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    packed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    out_for_delivery_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )

    status_history = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "subtotal >= 0",
            name="chk_order_subtotal",
        ),
        CheckConstraint(
            "delivery_fee >= 0",
            name="chk_order_delivery_fee",
        ),
        CheckConstraint(
            "discount_amount >= 0",
            name="chk_order_discount",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="chk_order_total",
        ),
    )