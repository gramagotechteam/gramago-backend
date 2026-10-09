from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.models.user import User

from app.services.delivery_partner_service import (
    DeliveryPartnerService,
)

from app.web.dependencies import (
    get_admin_web_user,
)

from app.web.templates import (
    templates,
)



from fastapi import (
    APIRouter,
    Depends,
    Form,
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

from app.services.delivery_partner_service import (
    DeliveryPartnerService,
)

from app.web.dependencies import (
    get_admin_web_user,
)


from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
)

from fastapi.responses import (
    RedirectResponse,
)

from pydantic import ValidationError

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User

from app.schemas.delivery_partner import (
    DeliveryPartnerCreate,
)

from app.services.delivery_partner_service import (
    DeliveryPartnerService,
)

from app.web.dependencies import (
    get_admin_web_user,
)

from app.web.templates import (
    templates,
)



from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
)



router = APIRouter(
    prefix="/delivery-partners",
)


# ============================================================
# DELIVERY PARTNER LIST
# ============================================================

@router.get("")
async def delivery_partner_list(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    partners = (
        await DeliveryPartnerService.list_all(
            db
        )
    )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/delivery_partners/list.html"
        ),

        context={
            "current_admin":
                current_admin,

            "partners":
                partners,

            "page_title":
                "Delivery Partners",

            "active_menu":
                "delivery_partners",
                "active_page": (
                                "delivery_partners"
                            ),
        },
    )
    
    


# ============================================================
# CREATE DELIVERY PARTNER PAGE
# ============================================================

@router.get("/create")
async def delivery_partner_create_page(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),
):

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/delivery_partners/create.html"
        ),

        context={
            "current_admin":
                current_admin,

            "page_title":
                "Add Delivery Partner",

            "active_menu":
                "delivery_partners",
                "active_page": (
                                                "delivery_partners"
                                            ),

            "form_data":
                {},

            "error":
                None,
        },
    )
    
    



# ============================================================
# CREATE DELIVERY PARTNER
# ============================================================

@router.post("/create")
async def delivery_partner_create(
    request: Request,

    full_name: str = Form(...),

    email: str = Form(""),

    phone: str = Form(...),

    password: str = Form(...),

    vehicle_type: str = Form(""),

    vehicle_number: str = Form(""),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    form_data = {
        "full_name":
            full_name,

        "email":
            email,

        "phone":
            phone,

        "vehicle_type":
            vehicle_type,

        "vehicle_number":
            vehicle_number,
    }

    try:

        data = DeliveryPartnerCreate(
            full_name=(
                full_name.strip()
            ),

            email=(
                email.strip()
                if email.strip()
                else None
            ),

            phone=(
                phone.strip()
            ),

            password=
                password,

            vehicle_type=(
                vehicle_type.strip()
                if vehicle_type.strip()
                else None
            ),

            vehicle_number=(
                vehicle_number.strip()
                if vehicle_number.strip()
                else None
            ),
        )

        await DeliveryPartnerService.create(
            db=db,
            data=data,
        )

        return RedirectResponse(
            url=(
                "/admin/delivery-partners"
                "?created=1"
            ),

            status_code=303,
        )

    except ValidationError as exc:

        error_message = (
            exc.errors()[0]["msg"]
            if exc.errors()
            else "Invalid form data."
        )

    except ValueError as exc:

        error_message = str(exc)

    except Exception:

        error_message = (
            "Unable to create delivery partner."
        )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/delivery_partners/create.html"
        ),

        context={
            "current_admin":
                current_admin,

            "page_title":
                "Add Delivery Partner",

            "active_menu":
                "delivery_partners",

            "form_data":
                form_data,
                "active_page": (
                                                "delivery_partners"
                                            ),

            "error":
                error_message,
        },

        status_code=400,
    )
    
    




# ============================================================
# DELIVERY PARTNER DETAIL
# ============================================================

@router.get("/{partner_id}")
async def delivery_partner_detail(
    partner_id: int,

    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    partner = (
        await DeliveryPartnerService.get_by_id(
            db=db,
            user_id=partner_id,
        )
    )

    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner not found.",
        )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/delivery_partners/detail.html"
        ),

        context={
            "current_admin":
                current_admin,

            "partner":
                partner,

            "profile":
                partner.delivery_profile,

            "page_title":
                "Delivery Partner Details",

            "active_menu":
                "delivery_partners",
                
                "active_page": (
                                                "delivery_partners"
                                            ),
        },
    )
    
    
    


# ============================================================
# APPROVE / UNAPPROVE DELIVERY PARTNER
# ============================================================

@router.post(
    "/{partner_id}/approval"
)
async def delivery_partner_approval(
    partner_id: int,

    approved: bool = Form(...),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    partner = (
        await DeliveryPartnerService.get_by_id(
            db=db,
            user_id=partner_id,
        )
    )

    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner not found.",
        )

    try:

        await DeliveryPartnerService.set_approval(
            db=db,
            user=partner,
            approved=approved,
        )

    except ValueError as exc:

        return RedirectResponse(
            url=(
                f"/admin/delivery-partners/"
                f"{partner_id}"
                f"?error={str(exc)}"
            ),
            status_code=303,
        )

    action = (
        "approved"
        if approved
        else "unapproved"
    )

    return RedirectResponse(
        url=(
            f"/admin/delivery-partners/"
            f"{partner_id}"
            f"?{action}=1"
        ),
        status_code=303,
    )
    
    
    



# ============================================================
# ACTIVATE / DEACTIVATE DELIVERY PARTNER
# ============================================================

@router.post(
    "/{partner_id}/active"
)
async def delivery_partner_active(
    partner_id: int,

    active: bool = Form(...),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    partner = (
        await DeliveryPartnerService.get_by_id(
            db=db,
            user_id=partner_id,
        )
    )

    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner not found.",
        )

    await DeliveryPartnerService.set_active(
        db=db,
        user=partner,
        active=active,
    )

    action = (
        "activated"
        if active
        else "deactivated"
    )

    return RedirectResponse(
        url=(
            f"/admin/delivery-partners/"
            f"{partner_id}"
            f"?{action}=1"
        ),
        status_code=303,
    )
    
    
    




# ============================================================
# CHANGE DELIVERY PARTNER PASSWORD
# ============================================================

@router.post(
    "/{partner_id}/change-password"
)
async def change_delivery_partner_password(
    partner_id: int,

    new_password: str = Form(...),
    confirm_password: str = Form(...),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    # --------------------------------------------------------
    # LOAD PARTNER
    # --------------------------------------------------------

    partner = (
        await DeliveryPartnerService
        .get_by_id(
            db,
            partner_id,
        )
    )

    if partner is None:

        return RedirectResponse(
            url=(
                "/admin/delivery-partners"
                "?error=partner_not_found"
            ),
            status_code=303,
        )

    # --------------------------------------------------------
    # VALIDATE PASSWORD
    # --------------------------------------------------------

    new_password = (
        new_password.strip()
    )

    confirm_password = (
        confirm_password.strip()
    )

    if len(new_password) < 8:

        return RedirectResponse(
            url=(
                f"/admin/delivery-partners/"
                f"{partner_id}"
                "?password_error=too_short"
            ),
            status_code=303,
        )

    if (
        new_password
        != confirm_password
    ):

        return RedirectResponse(
            url=(
                f"/admin/delivery-partners/"
                f"{partner_id}"
                "?password_error=mismatch"
            ),
            status_code=303,
        )

    # --------------------------------------------------------
    # CHANGE PASSWORD
    # --------------------------------------------------------

    try:

        await DeliveryPartnerService.change_password(
            db=db,
            user=partner,
            new_password=new_password,
        )

    except ValueError:

        return RedirectResponse(
            url=(
                f"/admin/delivery-partners/"
                f"{partner_id}"
                "?password_error=invalid"
            ),
            status_code=303,
        )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return RedirectResponse(
        url=(
            f"/admin/delivery-partners/"
            f"{partner_id}"
            "?password_changed=1"
        ),
        status_code=303,
    )