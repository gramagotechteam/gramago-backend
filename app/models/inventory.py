from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        unique=True,
        nullable=False,
    )

    available_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
        default=0,
    )

    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
        default=0,
    )

    reorder_level: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
        default=0,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    product = relationship(
        "Product",
        back_populates="inventory",
    )

    __table_args__ = (
        CheckConstraint(
            "available_quantity >= 0",
            name="chk_inventory_available",
        ),
        CheckConstraint(
            "reserved_quantity >= 0",
            name="chk_inventory_reserved",
        ),
        CheckConstraint(
            "reorder_level >= 0",
            name="chk_inventory_reorder",
        ),
        CheckConstraint(
            "reserved_quantity <= available_quantity",
            name="chk_inventory_reserved_not_excess",
        ),
    )