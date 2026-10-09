from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerUpdate,
    DeliveryPartnerApprovalUpdate,
    DeliveryPartnerActiveUpdate,
    DeliveryPartnerResponse,
)

from app.services.delivery_partner_service import (
    DeliveryPartnerService,
    delivery_partner_response,
)

# IMPORTANT:
# Change these imports to match your existing project
from app.db.session import get_db
# from app.api.deps import require_admin

from app.dependencies.auth import require_admin


router = APIRouter()


# ============================================================
# CREATE DELIVERY PARTNER
# ============================================================

@router.post(
    "",
    response_model=DeliveryPartnerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_delivery_partner(
    payload: DeliveryPartnerCreate,

    db: AsyncSession = Depends(get_db),

    current_admin=Depends(
        require_admin
    ),
):
    try:
        user = await DeliveryPartnerService.create(
            db,
            payload,
        )

        return delivery_partner_response(
            user
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ============================================================
# LIST DELIVERY PARTNERS
# ============================================================

@router.get(
    "",
    response_model=list[DeliveryPartnerResponse],
)
async def list_delivery_partners(
    db: AsyncSession = Depends(get_db),

    current_admin=Depends(
        require_admin
    ),
):
    users = await DeliveryPartnerService.list_all(
        db
    )

    return [
        delivery_partner_response(user)
        for user in users
    ]


# ============================================================
# GET ONE DELIVERY PARTNER
# ============================================================

@router.get(
    "/{partner_id}",
    response_model=DeliveryPartnerResponse,
)
async def get_delivery_partner(
    partner_id: int,

    db: AsyncSession = Depends(get_db),

    current_admin=Depends(
        require_admin
    ),
):
    user = await DeliveryPartnerService.get_by_id(
        db,
        partner_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner not found.",
        )

    return delivery_partner_response(
        user
    )


# ============================================================
# UPDATE
# ============================================================

@router.patch(
    "/{partner_id}",
    response_model=DeliveryPartnerResponse,
)
async def update_delivery_partner(
    partner_id: int,

    payload: DeliveryPartnerUpdate,

    db: AsyncSession = Depends(get_db),

    current_admin=Depends(
        require_admin
    ),
):
    user = await DeliveryPartnerService.get_by_id(
        db,
        partner_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner not found.",
        )

    try:
        user = await DeliveryPartnerService.update(
            db,
            user,
            payload,
        )

        return delivery_partner_response(
            user
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ============================================================
# APPROVE / REMOVE APPROVAL
# ============================================================

@router.patch(
    "/{partner_id}/approval",
    response_model=DeliveryPartnerResponse,
)
async def update_delivery_partner_approval(
    partner_id: int,

    payload: DeliveryPartnerApprovalUpdate,

    db: AsyncSession = Depends(get_db),

    current_admin=Depends(
        require_admin
    ),
):
    user = await DeliveryPartnerService.get_by_id(
        db,
        partner_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner not found.",
        )

    try:
        user = await DeliveryPartnerService.set_approval(
            db,
            user,
            payload.is_approved,
        )

        return delivery_partner_response(
            user
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ============================================================
# ACTIVATE / DEACTIVATE
# ============================================================

@router.patch(
    "/{partner_id}/active",
    response_model=DeliveryPartnerResponse,
)
async def update_delivery_partner_active(
    partner_id: int,

    payload: DeliveryPartnerActiveUpdate,

    db: AsyncSession = Depends(get_db),

    current_admin=Depends(
        require_admin
    ),
):
    user = await DeliveryPartnerService.get_by_id(
        db,
        partner_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner not found.",
        )

    user = await DeliveryPartnerService.set_active(
        db,
        user,
        payload.is_active,
    )

    return delivery_partner_response(
        user
    )
    
    
    


