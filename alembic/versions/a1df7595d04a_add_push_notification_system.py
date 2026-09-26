"""add push notification system

Revision ID: a1df7595d04a
Revises: d92fd2a6e165
Create Date: 2026-09-17 17:01:21.196441

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql




# revision identifiers, used by Alembic.
revision: str = 'a1df7595d04a'
down_revision: Union[str, Sequence[str], None] = 'd92fd2a6e165'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. New tables
    # ---------------------------------------------------------

    op.create_table(
        'device_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('fcm_token', sa.String(length=512), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('device_name', sa.String(length=150), nullable=True),
        sa.Column('app_version', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column(
            'last_seen_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'fcm_token',
            name='uq_device_tokens_fcm_token',
        ),
    )

    op.create_index(
        'ix_device_tokens_user_active',
        'device_tokens',
        ['user_id', 'is_active'],
        unique=False,
    )

    op.create_index(
        op.f('ix_device_tokens_user_id'),
        'device_tokens',
        ['user_id'],
        unique=False,
    )


    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column(
            'transactional_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'product_updates_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'price_alerts_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'promotions_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'general_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id',
            name='uq_notification_preferences_user',
        ),
    )

    op.create_index(
        op.f('ix_notification_preferences_user_id'),
        'notification_preferences',
        ['user_id'],
        unique=False,
    )


    # ---------------------------------------------------------
    # 2. Extend existing notifications table safely
    # ---------------------------------------------------------

    # Add required columns with temporary defaults so existing
    # rows receive valid values.

    op.add_column(
        'notifications',
        sa.Column(
            'category',
            sa.String(length=30),
            nullable=False,
            server_default='GENERAL',
        ),
    )

    op.add_column(
        'notifications',
        sa.Column(
            'action',
            sa.String(length=50),
            nullable=False,
            server_default='OPEN_NOTIFICATIONS',
        ),
    )

    op.add_column(
        'notifications',
        sa.Column(
            'image_url',
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        'notifications',
        sa.Column(
            'metadata_json',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


    # ---------------------------------------------------------
    # 3. Expand title length
    # ---------------------------------------------------------

    op.alter_column(
        'notifications',
        'title',
        existing_type=sa.VARCHAR(length=180),
        type_=sa.String(length=200),
        existing_nullable=False,
    )


    # ---------------------------------------------------------
    # 4. Index
    # ---------------------------------------------------------

    op.create_index(
        op.f('ix_notifications_category'),
        'notifications',
        ['category'],
        unique=False,
    )


    # ---------------------------------------------------------
    # 5. Remove temporary database defaults
    #
    # App-level defaults remain in SQLAlchemy model.
    # ---------------------------------------------------------

    op.alter_column(
        'notifications',
        'category',
        server_default=None,
    )

    op.alter_column(
        'notifications',
        'action',
        server_default=None,
    )

def downgrade() -> None:
    op.drop_index(
        op.f('ix_notifications_category'),
        table_name='notifications',
    )

    op.alter_column(
        'notifications',
        'title',
        existing_type=sa.String(length=200),
        type_=sa.VARCHAR(length=180),
        existing_nullable=False,
    )

    op.drop_column(
        'notifications',
        'metadata_json',
    )

    op.drop_column(
        'notifications',
        'image_url',
    )

    op.drop_column(
        'notifications',
        'action',
    )

    op.drop_column(
        'notifications',
        'category',
    )


    op.drop_index(
        op.f('ix_notification_preferences_user_id'),
        table_name='notification_preferences',
    )

    op.drop_table(
        'notification_preferences',
    )


    op.drop_index(
        op.f('ix_device_tokens_user_id'),
        table_name='device_tokens',
    )

    op.drop_index(
        'ix_device_tokens_user_active',
        table_name='device_tokens',
    )

    op.drop_table(
        'device_tokens',
    )