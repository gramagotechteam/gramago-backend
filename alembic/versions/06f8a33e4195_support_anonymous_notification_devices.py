"""support anonymous notification devices

Revision ID: 06f8a33e4195
Revises: a1df7595d04a
Create Date: 2026-09-17 18:38:38.252519
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "06f8a33e4195"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "a1df7595d04a"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    """Upgrade schema."""

    # =========================================================
    # 1. ADD allow_marketing SAFELY
    #
    # Existing rows already exist in device_tokens,
    # so use a temporary server default.
    # =========================================================

    op.add_column(
        "device_tokens",
        sa.Column(
            "allow_marketing",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )


    # =========================================================
    # 2. ALLOW ANONYMOUS DEVICES
    #
    # user_id can now be NULL.
    # =========================================================

    op.alter_column(
        "device_tokens",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )


    # =========================================================
    # 3. INDEX FOR PUBLIC / MARKETING NOTIFICATIONS
    # =========================================================

    op.create_index(
        "ix_device_tokens_marketing_active",
        "device_tokens",
        [
            "allow_marketing",
            "is_active",
        ],
        unique=False,
    )


    # =========================================================
    # 4. CHANGE USER FOREIGN KEY
    #
    # Old:
    # user deleted -> device token deleted
    #
    # New:
    # user deleted -> device remains anonymous
    # =========================================================

    op.drop_constraint(
        "device_tokens_user_id_fkey",
        "device_tokens",
        type_="foreignkey",
    )


    op.create_foreign_key(
        "fk_device_tokens_user_id_users",
        "device_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


    # =========================================================
    # 5. REMOVE TEMPORARY DATABASE DEFAULT
    #
    # SQLAlchemy model still handles default=True
    # for future rows.
    # =========================================================

    op.alter_column(
        "device_tokens",
        "allow_marketing",
        existing_type=sa.Boolean(),
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # =========================================================
    # 1. REMOVE NEW FOREIGN KEY
    # =========================================================

    op.drop_constraint(
        "fk_device_tokens_user_id_users",
        "device_tokens",
        type_="foreignkey",
    )


    # =========================================================
    # 2. RESTORE OLD FOREIGN KEY
    # =========================================================

    op.create_foreign_key(
        "device_tokens_user_id_fkey",
        "device_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


    # =========================================================
    # 3. REMOVE MARKETING INDEX
    # =========================================================

    op.drop_index(
        "ix_device_tokens_marketing_active",
        table_name="device_tokens",
    )


    # =========================================================
    # 4. HANDLE ANONYMOUS ROWS BEFORE MAKING user_id NOT NULL
    #
    # Important:
    # Anonymous rows cannot exist in the old schema.
    #
    # During downgrade we delete them first.
    # =========================================================

    op.execute(
        """
        DELETE FROM device_tokens
        WHERE user_id IS NULL
        """
    )


    # =========================================================
    # 5. MAKE user_id REQUIRED AGAIN
    # =========================================================

    op.alter_column(
        "device_tokens",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )


    # =========================================================
    # 6. REMOVE allow_marketing
    # =========================================================

    op.drop_column(
        "device_tokens",
        "allow_marketing",
    )