from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)


from app.schemas.delivery_workflow import (
    DeliveryRejectRequest,
    DeliveryCompleteRequest,
    DeliveryFailedRequest,
)


from app.db.session import get_db

from app.dependencies.delivery_auth import (
    get_current_delivery_partner,
)

from app.models.user import User

from app.services.delivery_order_service import (
    DeliveryOrderService,
    delivery_order_response,
)


from app.schemas.delivery_workflow import (
    DeliveryRejectRequest,
    DeliveryCompleteRequest,
)

from app.services.delivery_workflow_service import (
    DeliveryWorkflowService,
)

from app.services.delivery_assignment_service import (
    delivery_assignment_response,
)


router = APIRouter()


# ============================================================
# MY ACTIVE / ASSIGNED ORDERS
# ============================================================

@router.get(
    "/assigned"
)
async def assigned_orders(
    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    assignments = (
        await DeliveryOrderService
        .get_assigned_orders(
            db,
            current_partner,
        )
    )

    return {
        "success": True,

        "message": (
            "Assigned deliveries "
            "retrieved successfully"
        ),

        "data": [
            delivery_order_response(
                assignment
            )

            for assignment
            in assignments
        ],
    }



@router.get(
    "/active/current"
)
async def current_active_delivery(
    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignment = (
        await DeliveryOrderService
        .get_active_delivery(
            db,
            current_partner,
        )
    )

    return {
        "success": True,

        "message": (
            "Active delivery retrieved successfully"
        ),

        "data": (
            delivery_order_response(
                assignment
            )
            if assignment
            else None
        ),
    }
    




@router.get(
    "/history"
)
async def delivery_history(
    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignments = (
        await DeliveryOrderService
        .get_history(
            db,
            current_partner,
        )
    )

    return {
        "success": True,

        "message": (
            "Delivery history "
            "retrieved successfully"
        ),

        "data": [
            delivery_order_response(
                assignment
            )

            for assignment
            in assignments
        ],
    }
    
    
# =====
# 
# =======================================================
# ONE ORDER
# ============================================================

@router.get(
    "/{order_id}"
)
async def delivery_order_detail(
    order_id: int,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    assignment = (
        await DeliveryOrderService
        .get_order(
            db,
            current_partner,
            order_id,
        )
    )

    return {
        "success": True,

        "message": (
            "Delivery order retrieved successfully"
        ),

        "data": (
            delivery_order_response(
                assignment
            )
        ),
    }
    
    
    
    





@router.post(
    "/{order_id}/accept"
)
async def accept_delivery(
    order_id: int,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignment = (
        await DeliveryWorkflowService
        .accept(
            db,
            current_partner,
            order_id,
        )
    )

    return {
        "success": True,
        "message": (
            "Delivery accepted successfully"
        ),
        "data": (
            delivery_assignment_response(
                assignment
            )
        ),
    }
    
    
    


@router.post(
    "/{order_id}/reject"
)
async def reject_delivery(
    order_id: int,

    data: DeliveryRejectRequest,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignment = (
        await DeliveryWorkflowService
        .reject(
            db,
            current_partner,
            order_id,
            data.reason,
        )
    )

    return {
        "success": True,
        "message": (
            "Delivery rejected successfully"
        ),
        "data": (
            delivery_assignment_response(
                assignment
            )
        ),
    }
    
    
    
    


@router.post(
    "/{order_id}/picked-up"
)
async def mark_picked_up(
    order_id: int,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignment = (
        await DeliveryWorkflowService
        .mark_picked_up(
            db,
            current_partner,
            order_id,
        )
    )

    return {
        "success": True,
        "message": (
            "Order marked as picked up"
        ),
        "data": (
            delivery_assignment_response(
                assignment
            )
        ),
    }
    
    
    


@router.post(
    "/{order_id}/out-for-delivery"
)
async def start_delivery(
    order_id: int,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignment = (
        await DeliveryWorkflowService
        .start_delivery(
            db,
            current_partner,
            order_id,
        )
    )

    return {
        "success": True,
        "message": (
            "Order is out for delivery. "
            "Customer OTP has been sent."
        ),
        "data": (
            delivery_assignment_response(
                assignment
            )
        ),
    }
    
    
    


@router.post(
    "/{order_id}/complete"
)
async def complete_delivery(
    order_id: int,

    data: DeliveryCompleteRequest,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignment = (
        await DeliveryWorkflowService
        .complete_delivery(
            db=db,
            partner=current_partner,
            order_id=order_id,
            otp=data.otp,
            cod_collected_amount=(
                data.cod_collected_amount
            ),
        )
    )

    return {
        "success": True,

        "message": (
            "Order delivered successfully"
        ),

        "data": (
            delivery_assignment_response(
                assignment
            )
        ),
    }
    
    





@router.post(
    "/{order_id}/resend-otp"
)
async def resend_delivery_otp(
    order_id: int,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignment = (
        await DeliveryWorkflowService
        .resend_delivery_otp(
            db,
            current_partner,
            order_id,
        )
    )

    return {
        "success": True,

        "message": (
            "A new delivery OTP has "
            "been sent to the customer"
        ),

        "data": (
            delivery_assignment_response(
                assignment
            )
        ),
    }
    
    
    



@router.post(
    "/{order_id}/failed"
)
async def mark_delivery_failed(
    order_id: int,

    data: DeliveryFailedRequest,

    current_partner: User = Depends(
        get_current_delivery_partner
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    assignment = (
        await DeliveryWorkflowService
        .mark_failed(
            db,
            current_partner,
            order_id,
            data.reason,
        )
    )

    return {
        "success": True,

        "message": (
            "Delivery marked as failed"
        ),

        "data": (
            delivery_assignment_response(
                assignment
            )
        ),
    }
    
    


