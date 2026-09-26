from decimal import (
    Decimal,
    InvalidOperation,
)

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    RedirectResponse,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.session import get_db
from app.models.user import User

from app.services.commerce_settings_service import (
    CommerceSettingsService,
)

from app.web.csrf import (
    validate_csrf,
)
from app.web.dependencies import (
    get_admin_web_user,
)
from app.web.templates import templates


router = APIRouter()


# ============================================================
# COMMERCE SETTINGS PAGE
# ============================================================

@router.get(
    "/commerce-settings"
)
async def commerce_settings_page(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = (
        CommerceSettingsService(
            db
        )
    )

    settings = (
        await service.get_settings()
    )

    updated = (
        request.query_params.get(
            "updated"
        )
        == "1"
    )

    became_free = (
        request.query_params.get(
            "free"
        )
        == "1"
    )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/commerce_settings.html"
        ),

        context={
            "admin": current_admin,

            "settings": settings,

            "active_page": (
                "commerce_settings"
            ),

            "success": updated,

            "became_free_delivery": (
                became_free
            ),

            "error": None,
        },
    )


# ============================================================
# UPDATE COMMERCE SETTINGS
# ============================================================

@router.post(
    "/commerce-settings",
    dependencies=[
        Depends(
            validate_csrf
        )
    ],
)
async def update_commerce_settings(
    request: Request,

    minimum_order_amount: str = Form(
        ...
    ),

    delivery_fee: str = Form(
        ...
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = (
        CommerceSettingsService(
            db
        )
    )

    try:

        # ====================================================
        # PARSE VALUES
        # ====================================================

        try:

            minimum_value = Decimal(
                minimum_order_amount
                .strip()
            )

            delivery_value = Decimal(
                delivery_fee
                .strip()
            )

        except (
            InvalidOperation,
            ValueError,
        ):

            raise HTTPException(
                status_code=422,
                detail=(
                    "Enter valid numeric "
                    "amounts."
                ),
            )


        # ====================================================
        # BASIC WEB VALIDATION
        # ====================================================

        if minimum_value < 0:

            raise HTTPException(
                status_code=422,
                detail=(
                    "Minimum order amount "
                    "cannot be negative."
                ),
            )


        if delivery_value < 0:

            raise HTTPException(
                status_code=422,
                detail=(
                    "Delivery fee cannot "
                    "be negative."
                ),
            )


        # Numeric(10, 2)
        max_amount = Decimal(
            "99999999.99"
        )

        if minimum_value > max_amount:

            raise HTTPException(
                status_code=422,
                detail=(
                    "Minimum order amount "
                    "is too large."
                ),
            )


        if delivery_value > max_amount:

            raise HTTPException(
                status_code=422,
                detail=(
                    "Delivery fee is "
                    "too large."
                ),
            )


        # ====================================================
        # UPDATE
        # ====================================================

        (
            settings,
            became_free_delivery,
        ) = await service.update_settings(

            minimum_order_amount=(
                minimum_value
            ),

            delivery_fee=(
                delivery_value
            ),

            updated_by=(
                current_admin.id
            ),
        )


        # ====================================================
        # REDIRECT
        #
        # Prevent duplicate form submission on browser refresh.
        # ====================================================

        redirect_url = (
            "/admin/commerce-settings"
            "?updated=1"
        )

        if became_free_delivery:

            redirect_url += (
                "&free=1"
            )


        return RedirectResponse(
            url=redirect_url,
            status_code=303,
        )


    except HTTPException as exc:

        # Reload actual current values
        settings = (
            await service.get_settings()
        )

        return templates.TemplateResponse(
            request=request,

            name=(
                "admin/commerce_settings.html"
            ),

            context={
                "admin": current_admin,

                "settings": settings,

                "active_page": (
                    "commerce_settings"
                ),

                "success": False,

                "became_free_delivery": (
                    False
                ),

                "error": exc.detail,

                # Keep submitted values visible
                "submitted_minimum": (
                    minimum_order_amount
                ),

                "submitted_delivery": (
                    delivery_fee
                ),
            },

            status_code=(
                exc.status_code
            ),
        )