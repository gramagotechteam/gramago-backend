from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
)
from app.models.user import User
from app.repositories.admin_user_repository import (
    AdminUserRepository,
)
from app.services.audit_service import (
    AuditService,
)


class AdminUserService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.repository = (
            AdminUserRepository(db)
        )

        self.audit = AuditService(db)


    async def create_admin(
        self,
        *,
        full_name: str,
        email: str,
        phone: str,
        password: str,
        created_by: int,
    ):

        email = email.strip().lower()
        phone = phone.strip()

        result = await self.db.execute(
            select(User)
            .where(
                or_(
                    User.email == email,
                    User.phone == phone,
                )
            )
        )

        if result.scalar_one_or_none():

            raise HTTPException(
                status_code=409,
                detail=(
                    "Email or phone already exists"
                ),
            )

        user = User(
            full_name=full_name.strip(),
            email=email,
            phone=phone,
            password_hash=(
                hash_password(password)
            ),
            role="ADMIN",
            is_active=True,
            is_verified=True,
        )

        self.db.add(user)

        await self.db.flush()

        await self.audit.log(
            admin_user_id=created_by,
            action="ADMIN_CREATED",
            entity_type="USER",
            entity_id=user.id,
            description=(
                f"Admin account created for "
                f"{user.full_name}"
            ),
            new_data={
                "role": "ADMIN",
                "is_active": True,
            },
        )

        await self.db.commit()

        await self.db.refresh(user)

        return user


    async def set_active(
        self,
        *,
        user_id: int,
        is_active: bool,
        changed_by: int,
    ):

        user = (
            await self.repository
            .get_by_id(user_id)
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="Admin not found",
            )

        if user.id == changed_by:

            raise HTTPException(
                status_code=400,
                detail=(
                    "You cannot deactivate "
                    "your own account here"
                ),
            )

        old_value = user.is_active

        user.is_active = is_active

        await self.audit.log(
            admin_user_id=changed_by,
            action=(
                "ADMIN_ACTIVATED"
                if is_active
                else "ADMIN_DEACTIVATED"
            ),
            entity_type="USER",
            entity_id=user.id,
            old_data={
                "is_active": old_value,
            },
            new_data={
                "is_active": is_active,
            },
        )

        await self.db.commit()

        return user