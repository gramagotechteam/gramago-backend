# from fastapi import (
#     APIRouter,
#     Depends,
#     HTTPException,
#     status,
# )

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.schemas.delivery_auth import (
#     DeliveryLoginRequest,
#     DeliveryLoginResponse,
#     DeliveryPartnerMeResponse,
# )

# from app.services.delivery_auth_service import (
#     DeliveryAuthService,
# )

# from app.dependencies.delivery_auth import (
#     get_current_delivery_partner,
# )

# from app.models.user import User

# from app.db.session import get_db

# router = APIRouter()



# @router.post(
#     "/login",
#     response_model=DeliveryLoginResponse,
# )
# async def delivery_login(
#     payload: DeliveryLoginRequest,
#     db: AsyncSession = Depends(get_db),
# ):
#     user = await DeliveryAuthService.get_delivery_user(
#         db,
#         payload.identifier,
#     )

#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email/phone or password.",
#         )

#     if not verify_password(
#         payload.password,
#         user.password_hash,
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email/phone or password.",
#         )

#     DeliveryAuthService.validate_delivery_access(
#         user
#     )

#     access_token = create_access_token(
#         user_id=user.id,
#     )

#     refresh_token = await create_refresh_token(
#         db,
#         user.id,
#     )

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#         "user": delivery_user_response(user),
#     }
    




# @router.get(
#     "/me",
#     response_model=DeliveryPartnerMeResponse,
# )
# async def delivery_me(
#     current_user: User = Depends(
#         get_current_delivery_partner
#     ),
# ):
#     return delivery_user_response(
#         current_user
#     )
    
    
    

# def delivery_user_response(user: User) -> dict:

#     profile = user.delivery_profile

#     return {
#         "id": user.id,

#         "full_name": user.full_name,
#         "email": user.email,
#         "phone": user.phone,

#         "role": user.role,

#         "is_active": user.is_active,
#         "is_verified": user.is_verified,

#         "vehicle_type": profile.vehicle_type,
#         "vehicle_number": profile.vehicle_number,

#         "is_online": profile.is_online,
#         "is_available": profile.is_available,
#         "is_approved": profile.is_approved,

#         "created_at": user.created_at,
#     }





from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.core.rate_limit import (
    RateLimiter,
)

from app.db.session import get_db

from app.schemas.auth import (
    LoginRequest,
)

from app.schemas.delivery_partner import (
    DeliveryPartnerResponse,
)

from app.services.auth_service import (
    AuthService,
)

from app.services.delivery_partner_service import (
    delivery_partner_response,
)

from app.dependencies.delivery_auth import (
    get_current_delivery_partner,
)

from app.models.user import User


router = APIRouter()


# ============================================================
# RATE LIMIT
# ============================================================

delivery_login_limiter = RateLimiter(
    limit=5,
    window_seconds=60,
)


# ============================================================
# DELIVERY LOGIN
# ============================================================

@router.post(
    "/login"
)
async def delivery_login(
    data: LoginRequest,

    _: None = Depends(
        delivery_login_limiter
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        db
    )

    result = (
        await service.delivery_login(
            data.identifier,
            data.password,
        )
    )

    user = result.pop(
        "user"
    )

    return {
        "success": True,

        "message": (
            "Delivery partner login successful"
        ),

        "data": {
            **result,

            "user": (
                delivery_partner_response(
                    user
                )
            ),
        },
    }


# ============================================================
# CURRENT DELIVERY PARTNER
# ============================================================

@router.get(
    "/me",
    response_model=None,
)
async def delivery_me(
    current_partner: User = Depends(
        get_current_delivery_partner
    ),
):

    return {
        "success": True,

        "message": (
            "Delivery partner profile "
            "retrieved successfully"
        ),

        "data": (
            delivery_partner_response(
                current_partner
            )
        ),
    }