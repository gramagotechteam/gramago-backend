from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.admin_customer_repository import (
    AdminCustomerRepository,
)
from app.services.audit_service import (
    AuditService,
)
from datetime import datetime, timezone

from sqlalchemy import update

from app.models.refresh_token import (
    RefreshToken,
)

class AdminCustomerService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.repository = (
            AdminCustomerRepository(db)
        )

        self.audit_service = (
            AuditService(db)
        )


    # ==========================================
    # Deactivate
    # ==========================================

    async def deactivate(
        self,
        user_id: int,
        admin_id: int,
    ) -> User:

        try:

            customer = (
                await self.repository
                .get_customer(
                    user_id
                )
            )

            if not customer:

                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail="Customer not found",
                )

            if not customer.is_active:

                return customer


            customer.is_active = False


            await self.audit_service.log(

                admin_user_id=(
                    admin_id
                ),

                action=(
                    "CUSTOMER_DEACTIVATED"
                ),

                entity_type="USER",

                entity_id=(
                    customer.id
                ),

                description=(
                    f"Customer "
                    f"{customer.full_name} "
                    f"was deactivated"
                ),

                old_data={
                    "is_active": True
                },

                new_data={
                    "is_active": False
                },
            )
            
            
            await self.db.execute(
    update(RefreshToken)
    .where(
        RefreshToken.user_id
        == customer.id,

        RefreshToken.revoked_at
        .is_(None),
    )
    .values(
        revoked_at=datetime.now(
            timezone.utc
        )
    )
)


            await self.db.commit()

            await self.db.refresh(
                customer
            )

            return customer


        except HTTPException:

            await self.db.rollback()

            raise


        except Exception:

            await self.db.rollback()

            raise


    # ==========================================
    # Activate
    # ==========================================

    async def activate(
        self,
        user_id: int,
        admin_id: int,
    ) -> User:

        try:

            customer = (
                await self.repository
                .get_customer(
                    user_id
                )
            )

            if not customer:

                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail="Customer not found",
                )


            if customer.is_active:

                return customer


            customer.is_active = True


            await self.audit_service.log(

                admin_user_id=(
                    admin_id
                ),

                action=(
                    "CUSTOMER_ACTIVATED"
                ),

                entity_type="USER",

                entity_id=(
                    customer.id
                ),

                description=(
                    f"Customer "
                    f"{customer.full_name} "
                    f"was activated"
                ),

                old_data={
                    "is_active": False
                },

                new_data={
                    "is_active": True
                },
            )


            await self.db.commit()

            await self.db.refresh(
                customer
            )

            return customer


        except HTTPException:

            await self.db.rollback()

            raise


        except Exception:

            await self.db.rollback()

            raise