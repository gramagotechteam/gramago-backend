from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
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


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True,
    )

    sku: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    unit: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    unit_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        default=1,
    )

    min_order_qty: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        default=1,
    )

    max_order_qty: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
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

    category = relationship(
        "Category",
        back_populates="products",
    )

    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    inventory = relationship(
        "Inventory",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="chk_product_price",
        ),
        CheckConstraint(
            "discount_price IS NULL OR discount_price >= 0",
            name="chk_product_discount_price",
        ),
        CheckConstraint(
            "unit_value > 0",
            name="chk_product_unit_value",
        ),
        CheckConstraint(
            "min_order_qty > 0",
            name="chk_product_min_qty",
        ),
    )