# from fastapi import (
#     APIRouter,
#     Depends,
# )

# from sqlalchemy.ext.asyncio import (
#     AsyncSession,
# )

# from app.db.session import get_db

# from app.dependencies.auth import (
#     get_current_user,
# )

# from app.models.user import User

# from app.repositories.device_token_repository import (
#     DeviceTokenRepository,
# )

# from app.schemas.device_token import (
#     DeviceTokenRegisterRequest,
#     DeviceTokenRemoveRequest,
# )


# router = APIRouter()


# # ============================================================
# # REGISTER / REFRESH TOKEN
# # ============================================================

# @router.post("")
# async def register_device_token(

#     payload:
#         DeviceTokenRegisterRequest,

#     current_user:
#         User = Depends(
#             get_current_user
#         ),

#     db:
#         AsyncSession = Depends(
#             get_db
#         ),
# ):

#     repository = (
#         DeviceTokenRepository(
#             db
#         )
#     )


#     device = (
#         await repository.register(

#             user_id=(
#                 current_user.id
#             ),

#             token=payload.token,

#             platform=(
#                 payload.platform
#             ),

#             device_name=(
#                 payload.device_name
#             ),

#             app_version=(
#                 payload.app_version
#             ),
#         )
#     )


#     await db.commit()


#     await db.refresh(
#         device
#     )


#     return {

#         "success": True,

#         "message":
#             "Device registered successfully",

#         "data": {
#             "id":
#                 device.id,

#             "platform":
#                 device.platform,

#             "is_active":
#                 device.is_active,
#         },
#     }


# # ============================================================
# # LOGOUT / DEACTIVATE
# # ============================================================

# @router.delete("")
# async def deactivate_device_token(

#     payload:
#         DeviceTokenRemoveRequest,

#     current_user:
#         User = Depends(
#             get_current_user
#         ),

#     db:
#         AsyncSession = Depends(
#             get_db
#         ),
# ):

#     repository = (
#         DeviceTokenRepository(
#             db
#         )
#     )


#     await repository.deactivate_token(

#         user_id=(
#             current_user.id
#         ),

#         token=payload.token,
#     )


#     await db.commit()


#     return {

#         "success": True,

#         "message":
#             "Device notification token removed",

#         "data": None,
#     }
















from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.session import (
    get_db,
)

from app.dependencies.auth import (
    get_current_user,
)

from app.models.user import (
    User,
)

from app.repositories.device_token_repository import (
    DeviceTokenRepository,
)

from app.schemas.device_token import (
    DeviceTokenLinkRequest,
    DeviceTokenMarketingRequest,
    DeviceTokenRegisterRequest,
)


router = APIRouter()


# ============================================================
# PUBLIC DEVICE REGISTRATION
#
# Authentication NOT required.
#
# Called when:
# - app starts
# - first installation
# - FCM token changes while logged out
# ============================================================

@router.post("/register")
async def register_public_device(

    payload:
        DeviceTokenRegisterRequest,

    db:
        AsyncSession
        = Depends(get_db),
):

    repository = (
        DeviceTokenRepository(
            db
        )
    )


    device = (
        await repository.register_public(

            token=payload.token,

            platform=(
                payload.platform
            ),

            device_name=(
                payload.device_name
            ),

            app_version=(
                payload.app_version
            ),
        )
    )


    await db.commit()

    await db.refresh(
        device
    )


    return {

        "success": True,

        "message":
            "Device registered successfully",

        "data": {

            "id":
                device.id,

            "linked_user":
                device.user_id
                is not None,

            "is_active":
                device.is_active,

            "allow_marketing":
                device.allow_marketing,
        },
    }


# ============================================================
# LINK DEVICE TO AUTHENTICATED USER
#
# Called after login/register.
# ============================================================

@router.post("/link")
async def link_device_to_user(

    payload:
        DeviceTokenLinkRequest,

    current_user:
        User = Depends(
            get_current_user
        ),

    db:
        AsyncSession
        = Depends(get_db),
):

    repository = (
        DeviceTokenRepository(
            db
        )
    )


    device = (
        await repository.link_to_user(

            user_id=(
                current_user.id
            ),

            token=(
                payload.token
            ),
        )
    )


    await db.commit()

    await db.refresh(
        device
    )


    return {

        "success": True,

        "message":
            "Device linked to user",

        "data": {

            "id":
                device.id,

            "user_id":
                device.user_id,

            "is_active":
                device.is_active,
        },
    }


# ============================================================
# LOGOUT / DETACH
#
# Device remains active for public notifications.
# ============================================================

# @router.post("/detach")
# async def detach_device_from_user(

#     payload:
#         DeviceTokenLinkRequest,

#     current_user:
#         User = Depends(
#             get_current_user
#         ),

#     db:
#         AsyncSession
#         = Depends(get_db),
# ):

#     repository = (
#         DeviceTokenRepository(
#             db
#         )
#     )


#     await repository.detach_from_user(

#         user_id=(
#             current_user.id
#         ),

#         token=(
#             payload.token
#         ),
#     )


#     await db.commit()


#     return {

#         "success": True,

#         "message":
#             "Device detached from user",

#         "data": {

#             "still_receives_public_notifications":
#                 True,
#         },
#     }



@router.post("/detach")
async def detach_device_from_user(
    payload: DeviceTokenLinkRequest,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    repository = DeviceTokenRepository(
        db
    )

    await repository.detach_from_user(
        user_id=current_user.id,
        token=payload.token,
    )

    await db.commit()
    
    print("detached......................111111111111111111111111222222222222223333333333333333")

    return {
        "success": True,
        "message": "Device detached from user",
        "data": {
            "still_receives_public_notifications":
                True,
        },
    }
# ============================================================
# DEVICE MARKETING PREFERENCE
#
# Public endpoint because anonymous devices have no JWT.
# ============================================================

@router.patch("/marketing")
async def update_marketing_preference(

    payload:
        DeviceTokenMarketingRequest,

    db:
        AsyncSession
        = Depends(get_db),
):

    repository = (
        DeviceTokenRepository(
            db
        )
    )


    await repository.set_marketing_preference(

        token=payload.token,

        allow_marketing=(
            payload.allow_marketing
        ),
    )


    await db.commit()


    return {

        "success": True,

        "message":
            "Notification preference updated",

        "data": {

            "allow_marketing":
                payload.allow_marketing,
        },
    }