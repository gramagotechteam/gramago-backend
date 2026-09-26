# from fastapi import (
#     Depends,
#     HTTPException,
#     Request,
#     status,
# )
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db
# from app.models.user import User
# from app.repositories.user_repository import (
#     UserRepository,
# )


# async def get_admin_web_user(
#     request: Request,
#     db: AsyncSession = Depends(get_db),
# ) -> User:

#     user_id = request.session.get(
#         "admin_user_id"
#     )

#     if not user_id:

#         raise HTTPException(
#             status_code=status.HTTP_303_SEE_OTHER,
#             headers={
#                 "Location": "/admin/login"
#             },
#         )

#     repository = UserRepository(db)

#     user = await repository.get_by_id(
#         int(user_id)
#     )

#     if not user:

#         request.session.clear()

#         raise HTTPException(
#             status_code=status.HTTP_303_SEE_OTHER,
#             headers={
#                 "Location": "/admin/login"
#             },
#         )

#     if not user.is_active:

#         request.session.clear()

#         raise HTTPException(
#             status_code=status.HTTP_303_SEE_OTHER,
#             headers={
#                 "Location": "/admin/login"
#             },
#         )

#     if user.role not in {
#         "ADMIN",
#         "SUPER_ADMIN",
#     }:

#         request.session.clear()

#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Admin access required",
#         )

#     return user


# async def get_super_admin_web_user(
#     current_admin: User = Depends(
#         get_admin_web_user
#     ),
# ) -> User:

#     if (
#         current_admin.role
#         != "SUPER_ADMIN"
#     ):

#         raise HTTPException(
#             status_code=(
#                 status.HTTP_403_FORBIDDEN
#             ),
#             detail=(
#                 "Super Admin access required"
#             ),
#         )

#     return current_admin


from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)


async def get_admin_web_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:

    user_id = request.session.get(
        "admin_user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={
                "Location": "/admin/login"
            },
        )

    repository = UserRepository(db)

    user = await repository.get_by_id(
        int(user_id)
    )

    if not user:

        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={
                "Location": "/admin/login"
            },
        )

    if not user.is_active:

        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={
                "Location": "/admin/login"
            },
        )

    role = (
        user.role.strip().upper()
        if user.role
        else ""
    )

    if role not in {
        "ADMIN",
        "SUPER_ADMIN",
    }:

        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user


async def get_super_admin_web_user(
    current_admin: User = Depends(
        get_admin_web_user
    ),
) -> User:

    role = (
        current_admin.role.strip().upper()
        if current_admin.role
        else ""
    )

    if role != "SUPER_ADMIN":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required",
        )

    return current_admin