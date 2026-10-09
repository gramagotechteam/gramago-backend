from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)


from app.db.base import Base


class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # =========================================================
    # ORDER
    # =========================================================

    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # =========================================================
    # DELIVERY PARTNER
    # =========================================================

    delivery_partner_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # =========================================================
    # ASSIGNMENT STATUS
    #
    # ASSIGNED
    # ACCEPTED
    # REJECTED
    # PICKED_UP
    # OUT_FOR_DELIVERY
    # DELIVERED
    # FAILED
    # CANCELLED
    # =========================================================

    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="ASSIGNED",
        index=True,
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    picked_up_at: Mapped[datetime | None] = mapped_column(
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

    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================================================
    # NOTES
    # =========================================================

    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    delivery_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    
    # ============================================================
    # DELIVERY OTP
    # ============================================================

    delivery_otp_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    delivery_otp_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivery_otp_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0,
    )

    delivery_otp_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


    # ============================================================
    # COD
    # ============================================================

    cod_collected_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    cod_collected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================================================
    # CREATED / UPDATED
    # =========================================================

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
    
    
    delivery_otp_sent_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
)

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    order = relationship(
        "Order",
        back_populates="delivery_assignments",
    )

    delivery_partner = relationship(
    "User",
    back_populates="delivery_assignments",
    foreign_keys=[delivery_partner_id],
)
    __table_args__ = (
        Index(
            "ix_delivery_assignments_partner_status",
            "delivery_partner_id",
            "status",
        ),
        Index(
            "ix_delivery_assignments_order_status",
            "order_id",
            "status",
        ),
    )
    
    
    