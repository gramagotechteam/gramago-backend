# from fastapi import (
#     APIRouter,
#     Depends,
# )

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db

# from app.models.user import User

# from app.schemas.delivery_assignment import (
#     DeliveryOrderAssignRequest,
# )

# from app.services.delivery_assignment_service import (
#     DeliveryAssignmentService,
#     delivery_assignment_response,
# )

# # Use the same dependency already working
# # in admin_delivery_partners.py
# from app.dependencies.auth import (
#     get_current_user,
# )


# router = APIRouter()


# # ============================================================
# # AVAILABLE DELIVERY PARTNERS
# # ============================================================

# @router.get(
#     "/available-partners"
# )
# async def available_delivery_partners(
#     _: User = Depends(
#         get_current_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):
#     partners = (
#         await DeliveryAssignmentService
#         .get_available_partners(
#             db
#         )
#     )

#     data = []

#     for partner in partners:

#         profile = (
#             partner.delivery_profile
#         )

#         data.append(
#             {
#                 "id": partner.id,

#                 "full_name": (
#                     partner.full_name
#                 ),

#                 "phone": (
#                     partner.phone
#                 ),

#                 "vehicle_type": (
#                     profile.vehicle_type
#                 ),

#                 "vehicle_number": (
#                     profile.vehicle_number
#                 ),

#                 "is_online": (
#                     profile.is_online
#                 ),

#                 "is_available": (
#                     profile.is_available
#                 ),

#                 "current_latitude": (
#                     float(
#                         profile.current_latitude
#                     )
#                     if profile.current_latitude
#                     is not None
#                     else None
#                 ),

#                 "current_longitude": (
#                     float(
#                         profile.current_longitude
#                     )
#                     if profile.current_longitude
#                     is not None
#                     else None
#                 ),

#                 "last_location_at": (
#                     profile.last_location_at
#                 ),
#             }
#         )

#     return {
#         "success": True,

#         "message": (
#             "Available delivery partners "
#             "retrieved successfully"
#         ),

#         "data": data,
#     }


# # ============================================================
# # ASSIGN ORDER
# # ============================================================

# @router.post(
#     "/assign"
# )
# async def assign_delivery_partner(
#     data: DeliveryOrderAssignRequest,

#     current_admin: User = Depends(
#         get_current_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):
#     assignment = (
#         await DeliveryAssignmentService
#         .assign_order(
#             db=db,

#             order_id=(
#                 data.order_id
#             ),

#             partner_id=(
#                 data.delivery_partner_id
#             ),

#             admin_user=(
#                 current_admin
#             ),

#             delivery_note=(
#                 data.delivery_note
#             ),
#         )
#     )

#     return {
#         "success": True,

#         "message": (
#             "Delivery partner assigned successfully"
#         ),

#         "data": (
#             delivery_assignment_response(
#                 assignment
#             )
#         ),
#     }


# # ============================================================
# # ORDER ASSIGNMENT HISTORY
# # ============================================================

# @router.get(
#     "/order/{order_id}"
# )
# async def get_order_assignments(
#     order_id: int,

#     _: User = Depends(
#         get_current_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):
#     order = (
#         await DeliveryAssignmentService
#         .get_order(
#             db,
#             order_id,
#         )
#     )

#     return {
#         "success": True,

#         "message": (
#             "Delivery assignments retrieved successfully"
#         ),

#         "data": [
#             delivery_assignment_response(
#                 assignment
#             )
#             for assignment
#             in order.delivery_assignments
#         ],
#     }



from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.models.user import User

from app.schemas.delivery_assignment import (
    DeliveryOrderAssignRequest,
)

from app.services.delivery_assignment_service import (
    DeliveryAssignmentService,
    delivery_assignment_response,
)

from app.dependencies.auth import (
    get_current_user,
)


router = APIRouter()


# ============================================================
# ASSIGNABLE DELIVERY PARTNERS
# ============================================================

@router.get(
    "/available-partners"
)
async def available_delivery_partners(
    _: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Current version:
    Returns all active + approved + online delivery partners.

    A busy partner is still returned and can receive more orders.
    active_delivery_count tells admin how many active deliveries the
    partner currently has.
    """

    partners = (
        await DeliveryAssignmentService
        .get_available_partners(
            db
        )
    )

    data = []

    for partner in partners:
        profile = partner.delivery_profile

        active_delivery_count = (
            await DeliveryAssignmentService
            .get_active_delivery_count(
                db,
                partner.id,
            )
        )

        data.append(
            {
                "id": partner.id,

                "full_name": partner.full_name,

                "phone": partner.phone,

                "vehicle_type": (
                    profile.vehicle_type
                ),

                "vehicle_number": (
                    profile.vehicle_number
                ),

                "is_online": (
                    profile.is_online
                ),

                # Kept for UI compatibility.
                # False simply means the partner currently has active work.
                "is_available": (
                    profile.is_available
                ),

                "active_delivery_count": (
                    active_delivery_count
                ),

                "current_latitude": (
                    float(
                        profile.current_latitude
                    )
                    if profile.current_latitude
                    is not None
                    else None
                ),

                "current_longitude": (
                    float(
                        profile.current_longitude
                    )
                    if profile.current_longitude
                    is not None
                    else None
                ),

                "last_location_at": (
                    profile.last_location_at
                ),
            }
        )

    return {
        "success": True,

        "message": (
            "Assignable delivery partners "
            "retrieved successfully"
        ),

        "data": data,
    }


# ============================================================
# ASSIGN ORDER
# ============================================================

@router.post(
    "/assign"
)
async def assign_delivery_partner(
    data: DeliveryOrderAssignRequest,

    current_admin: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    assignment = (
        await DeliveryAssignmentService
        .assign_order(
            db=db,

            order_id=(
                data.order_id
            ),

            partner_id=(
                data.delivery_partner_id
            ),

            admin_user=(
                current_admin
            ),

            delivery_note=(
                data.delivery_note
            ),
        )
    )

    return {
        "success": True,

        "message": (
            "Delivery partner assigned successfully"
        ),

        "data": (
            delivery_assignment_response(
                assignment
            )
        ),
    }


# ============================================================
# ORDER ASSIGNMENT HISTORY
# ============================================================

@router.get(
    "/order/{order_id}"
)
async def get_order_assignments(
    order_id: int,

    _: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    order = (
        await DeliveryAssignmentService
        .get_order(
            db,
            order_id,
        )
    )

    return {
        "success": True,

        "message": (
            "Delivery assignments retrieved successfully"
        ),

        "data": [
            delivery_assignment_response(
                assignment
            )
            for assignment
            in order.delivery_assignments
        ],
    }
