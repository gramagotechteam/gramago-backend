from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_audit_log import (
    AdminAuditLog,
)


class AuditService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


    async def log(
        self,
        *,
        admin_user_id: int,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        description: str | None = None,
        old_data: dict | None = None,
        new_data: dict | None = None,
        ip_address: str | None = None,
    ):

        log = AdminAuditLog(
            admin_user_id=admin_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
        )

        self.db.add(log)

        return log