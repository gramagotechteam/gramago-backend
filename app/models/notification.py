# from datetime import datetime

# from sqlalchemy import (
#     Boolean,
#     DateTime,
#     ForeignKey,
#     String,
#     Text,
#     func,
# )
# from sqlalchemy.orm import (
#     Mapped,
#     mapped_column,
# )

# from app.db.base import Base


# class Notification(Base):
#     __tablename__ = "notifications"

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

#     notification_type: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         index=True,
#     )

#     title: Mapped[str] = mapped_column(
#         String(180),
#         nullable=False,
#     )

#     message: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     reference_type: Mapped[str | None] = mapped_column(
#         String(50),
#         nullable=True,
#     )

#     reference_id: Mapped[int | None] = mapped_column(
#         nullable=True,
#     )

#     is_read: Mapped[bool] = mapped_column(
#         Boolean,
#         nullable=False,
#         default=False,
#         index=True,
#     )

#     read_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#         index=True,
#     )




from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class Notification(Base):

    __tablename__ = "notifications"


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
    # WHY THE NOTIFICATION EXISTS
    # =========================================================

    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )


    # TRANSACTIONAL
    # PRODUCTS
    # PRICE_ALERTS
    # PROMOTIONS
    # GENERAL

    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="GENERAL",
        index=True,
    )


    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )


    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    # =========================================================
    # TAP ACTION
    # =========================================================

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="OPEN_NOTIFICATIONS",
    )


    # PRODUCT / ORDER / CATEGORY / OFFER etc.
    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )


    reference_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )


    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    # Flexible future data.
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )


    # =========================================================
    # READ STATUS
    # =========================================================

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )


    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )