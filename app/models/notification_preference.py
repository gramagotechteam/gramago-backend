from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class NotificationPreference(Base):

    __tablename__ = "notification_preferences"


    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )


    user_id: Mapped[int] = mapped_column(

        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),

        nullable=False,

        index=True,
    )


    # =========================================================
    # TRANSACTIONAL
    #
    # order placed, confirmed, packed, delivery, cancellation
    # =========================================================

    transactional_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


    # =========================================================
    # PRODUCT UPDATES
    #
    # new product, restock, category arrivals
    # =========================================================

    product_updates_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


    # =========================================================
    # PRICE ALERTS
    #
    # price drop etc.
    # =========================================================

    price_alerts_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


    # =========================================================
    # PROMOTIONS
    #
    # offers / discounts / campaigns
    # =========================================================

    promotions_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


    # =========================================================
    # GENERAL
    #
    # account / system / announcements
    # =========================================================

    general_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

        UniqueConstraint(
            "user_id",
            name="uq_notification_preferences_user",
        ),

    )