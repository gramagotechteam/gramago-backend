# from fastapi import APIRouter, Depends

# from app.dependencies.auth import get_current_user
# from app.models.user import User
# from app.schemas.user import UserResponse


# router = APIRouter()


# @router.get("/me")
# async def get_me(
#     current_user: User = Depends(get_current_user),
# ):
#     return {
#         "success": True,
#         "message": "User fetched successfully",
#         "data": UserResponse.model_validate(
#             current_user
#         ),
#     }





from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserUpdate,
)

from app.services.user_service import (
    UserService,
)


router = APIRouter()


@router.get("/me")
async def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return {
        "success": True,
        "message": "User fetched successfully",
        "data": UserResponse.model_validate(
            current_user
        ),
    }



@router.patch("/me")
async def update_me(
    data: UserUpdate,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = UserService(
        db
    )

    user = await service.update_profile(
        current_user,
        data,
    )

    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": UserResponse.model_validate(
            user
        ),
    }

# @router.patch("/me")
# async def update_me(
#     data: UserUpdate,
#     current_user: User = Depends(
#         get_current_user
#     ),
#     db: AsyncSession = Depends(get_db),
# ):

#     service = UserService(db)

#     user, email_changed = (
#         await service.update_profile(
#             current_user,
#             data,
#         )
#     )

#     if email_changed:

#         auth_service = AuthService(db)

#         try:
#             await auth_service.send_verification(
#                 user
#             )
#         except Exception:
#             pass

#     return {
#         "success": True,
#         "message": "Profile updated successfully",
#         "data": UserResponse.model_validate(
#             user
#         ),
#     }