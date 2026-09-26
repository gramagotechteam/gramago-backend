# from fastapi import HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.user import User
# from app.repositories.user_repository import (
#     UserRepository,
# )
# from app.schemas.user import UserUpdate


# class UserService:

#     def __init__(
#         self,
#         db: AsyncSession,
#     ):
#         self.db = db
#         self.users = UserRepository(db)


#     async def update_profile(
#         self,
#         user: User,
#         data: UserUpdate,
#     ) -> tuple[User, bool]:

#         email_changed = False

#         if data.full_name is not None:

#             user.full_name = (
#                 data.full_name.strip()
#             )


#         if data.email is not None:

#             new_email = (
#                 str(data.email)
#                 .lower()
#                 .strip()
#             )

#             if new_email != user.email:

#                 existing = (
#                     await self.users.get_by_email(
#                         new_email
#                     )
#                 )

#                 if existing and existing.id != user.id:

#                     raise HTTPException(
#                         status_code=(
#                             status.HTTP_409_CONFLICT
#                         ),
#                         detail=(
#                             "Email already registered"
#                         ),
#                     )

#                 user.email = new_email

#                 # New email must be verified
#                 # user.is_verified = False

#                 email_changed = True


#         await self.db.commit()

#         await self.db.refresh(user)

#         return user, email_changed






from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db
        self.users = UserRepository(db)

    async def update_profile(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:

        # =====================================================
        # FULL NAME
        # =====================================================

        if data.full_name is not None:

            full_name = (
                data.full_name
                .strip()
            )

            if len(full_name) < 2:
                raise HTTPException(
                    status_code=(
                        status.HTTP_422_UNPROCESSABLE_ENTITY
                    ),
                    detail=(
                        "Full name must be at least "
                        "2 characters"
                    ),
                )

            user.full_name = full_name

        # =====================================================
        # EMAIL
        #
        # Phone verification is NOT affected by changing email.
        # =====================================================

        if data.email is not None:

            new_email = (
                str(data.email)
                .lower()
                .strip()
            )

            if new_email != user.email:

                existing = (
                    await self.users
                    .get_by_email(
                        new_email
                    )
                )

                if (
                    existing
                    and
                    existing.id != user.id
                ):
                    raise HTTPException(
                        status_code=(
                            status.HTTP_409_CONFLICT
                        ),
                        detail=(
                            "Email already registered"
                        ),
                    )

                user.email = new_email

        await self.db.commit()

        await self.db.refresh(
            user
        )

        return user