from sqlalchemy import (
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_audit_log import (
    AdminAuditLog,
)
from app.models.user import User


class AdminAuditRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    # ==========================================
    # List logs
    # ==========================================

    async def list_logs(
        self,
        *,
        search: str | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        admin_user_id: int | None = None,
        page: int = 1,
        limit: int = 25,
    ):

        conditions = []

        if search:

            keyword = (
                f"%{search.strip()}%"
            )

            conditions.append(
                or_(
                    AdminAuditLog.action.ilike(
                        keyword
                    ),

                    AdminAuditLog.entity_type.ilike(
                        keyword
                    ),

                    AdminAuditLog.description.ilike(
                        keyword
                    ),
                )
            )


        if action:

            conditions.append(
                AdminAuditLog.action
                == action
            )


        if entity_type:

            conditions.append(
                AdminAuditLog.entity_type
                == entity_type
            )


        if admin_user_id:

            conditions.append(
                AdminAuditLog.admin_user_id
                == admin_user_id
            )


        count_result = await self.db.execute(
            select(
                func.count(
                    AdminAuditLog.id
                )
            )
            .where(
                *conditions
            )
        )

        total = (
            count_result.scalar_one()
        )


        result = await self.db.execute(
            select(
                AdminAuditLog,
                User,
            )
            .outerjoin(
                User,
                User.id
                == AdminAuditLog.admin_user_id,
            )
            .where(
                *conditions
            )
            .order_by(
                AdminAuditLog.created_at.desc()
            )
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
        )


        rows = result.all()

        return rows, total


    # ==========================================
    # Single log
    # ==========================================

    async def get_by_id(
        self,
        log_id: int,
    ):

        result = await self.db.execute(
            select(
                AdminAuditLog,
                User,
            )
            .outerjoin(
                User,
                User.id
                == AdminAuditLog.admin_user_id,
            )
            .where(
                AdminAuditLog.id
                == log_id
            )
        )

        return result.first()


    # ==========================================
    # Distinct actions
    # ==========================================

    async def get_actions(
        self,
    ):

        result = await self.db.execute(
            select(
                AdminAuditLog.action
            )
            .distinct()
            .order_by(
                AdminAuditLog.action
            )
        )

        return [
            row[0]
            for row in result.all()
        ]


    # ==========================================
    # Distinct entity types
    # ==========================================

    async def get_entity_types(
        self,
    ):

        result = await self.db.execute(
            select(
                AdminAuditLog.entity_type
            )
            .distinct()
            .order_by(
                AdminAuditLog.entity_type
            )
        )

        return [
            row[0]
            for row in result.all()
        ]


    # ==========================================
    # Admin users
    # ==========================================

    async def get_admin_users(
        self,
    ):

        result = await self.db.execute(
            select(User)
            .where(
                User.role.in_(
                    [
                        "ADMIN",
                        "SUPER_ADMIN",
                    ]
                )
            )
            .order_by(
                User.full_name
            )
        )

        return result.scalars().all()