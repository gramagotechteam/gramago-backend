# from datetime import datetime

# from sqlalchemy import (
#     Boolean,
#     DateTime,
#     ForeignKey,
#     Index,
#     String,
#     UniqueConstraint,
#     func,
# )

# from sqlalchemy.orm import (
#     Mapped,
#     mapped_column,
#     relationship,
# )

# from app.db.base import Base


# class DeviceToken(Base):

#     __tablename__ = "device_tokens"


#     id: Mapped[int] = mapped_column(
#         primary_key=True,
#         autoincrement=True,
#     )


#     user_id: Mapped[int] = mapped_column(

#         ForeignKey(
#             "users.id",
#             ondelete="CASCADE",
#         ),

#         nullable=False,

#         index=True,
#     )


#     # Firebase Cloud Messaging token
#     fcm_token: Mapped[str] = mapped_column(
#         String(512),
#         nullable=False,
#         unique=True,
#     )


#     platform: Mapped[str] = mapped_column(
#         String(20),
#         nullable=False,
#         default="android",
#     )


#     device_name: Mapped[str | None] = mapped_column(
#         String(150),
#         nullable=True,
#     )


#     app_version: Mapped[str | None] = mapped_column(
#         String(50),
#         nullable=True,
#     )


#     is_active: Mapped[bool] = mapped_column(
#         Boolean,
#         nullable=False,
#         default=True,
#     )


#     last_seen_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#     )


#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#     )


#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#         onupdate=func.now(),
#     )


#     user = relationship(
#         "User",
#         back_populates="device_tokens",
#     )


#     __table_args__ = (

#         Index(
#             "ix_device_tokens_user_active",
#             "user_id",
#             "is_active",
#         ),

#         UniqueConstraint(
#             "fcm_token",
#             name="uq_device_tokens_fcm_token",
#         ),
#     )









from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


class DeviceToken(Base):

    __tablename__ = "device_tokens"


    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )


    # =========================================================
    # USER
    #
    # NULL  -> anonymous installation
    # VALUE -> currently linked logged-in user
    # =========================================================

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )


    # =========================================================
    # FCM TOKEN
    # =========================================================

    fcm_token: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )


    platform: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="android",
    )


    device_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )


    app_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )


    # =========================================================
    # DEVICE STATUS
    # =========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


    # Public offers / products / promotions.
    allow_marketing: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
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


    user = relationship(
        "User",
        back_populates="device_tokens",
    )


    __table_args__ = (

        UniqueConstraint(
            "fcm_token",
            name="uq_device_tokens_fcm_token",
        ),

        Index(
            "ix_device_tokens_user_active",
            "user_id",
            "is_active",
        ),

        Index(
            "ix_device_tokens_marketing_active",
            "allow_marketing",
            "is_active",
        ),
    )