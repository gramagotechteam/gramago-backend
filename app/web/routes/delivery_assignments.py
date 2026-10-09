# # from fastapi import (
# #     APIRouter,
# #     Depends,
# #     Request,
# # )

# # from sqlalchemy import (
# #     select,
# # )

# # from sqlalchemy.ext.asyncio import (
# #     AsyncSession,
# # )

# # from app.db.session import (
# #     get_db,
# # )

# # from app.models.order import (
# #     Order,
# # )

# # from app.models.user import (
# #     User,
# # )

# # from app.web.dependencies import (
# #     get_admin_web_user,
# # )

# # from app.web.templates import (
# #     templates,
# # )


# # from curses import flash

# from app.models.delivery_assignment import (
#     DeliveryAssignment,
# )

# from app.models.delivery_partner import (
#     DeliveryPartnerProfile,
# )

# from app.models.order import Order
# from app.models.user import User

# from datetime import datetime, timezone

# from fastapi import (
#     APIRouter,
#     Depends,
#     Form,
#     HTTPException,
#     Request,
#     status,
# )

# from fastapi.responses import (
#     RedirectResponse,
# )

# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db

# from app.models.order import Order
# from app.models.user import User

# from app.services.delivery_assignment_service import (
#     DeliveryAssignmentService,
# )


# from sqlalchemy import (
#     func,
#     or_,
#     select,
# )


# from app.web.dependencies import (
#     get_admin_web_user,
# )

# from app.web.templates import templates


# from sqlalchemy import (
#     select,
# )

# from app.models.user import User

# from app.services.delivery_assignment_service import (
#     DeliveryAssignmentService,
# )



# from collections import Counter
# from datetime import datetime, timezone

# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.delivery_assignment import (
#     DeliveryAssignment,
# )

# from app.models.delivery_partner import (
#     DeliveryPartnerProfile,
# )

# from app.models.order import Order
# from app.models.user import User

# ACTIVE_DELIVERY_STATUSES = {
#     "ASSIGNED",
#     "ACCEPTED",
#     "PICKED_UP",
#     "OUT_FOR_DELIVERY",
# }

# TERMINAL_DELIVERY_STATUSES = {
#     "DELIVERED",
#     "REJECTED",
#     "FAILED",
#     "CANCELLED",
# }



# router = APIRouter(
#     prefix="/delivery-assignments",
# )


# # ============================================================
# # READY FOR DELIVERY ORDERS
# # ============================================================

# @router.get("/ready")
# async def ready_for_delivery_orders(
#     request: Request,

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):
    
    
#     partners = (
#     await DeliveryAssignmentService
#     .get_available_partners(
#         db
#     )
# )
    
    
    

#     partner_options = []

#     for partner in partners:

#         active_count = (
#             await DeliveryAssignmentService
#             .get_active_delivery_count(
#                 db,
#                 partner.id,
#             )
#         )

#         partner_options.append(
#             {
#                 "partner":
#                     partner,

#                 "active_count":
#                     active_count,
#             }
#         )
        
        
    
#     partner_options.sort(
#     key=lambda item: (
#         item["active_count"],
#         item["partner"].full_name.lower(),
#     )
# )

#     result = await db.execute(
#         select(Order)
#         .where(
#             Order.order_status.in_(
#                 [
#                     "PACKED",
#                     "READY_FOR_PICKUP",
#                 ]
#             )
#         )
#         .order_by(
#             Order.created_at.asc()
#         )
#     )

#     orders = list(
#         result.scalars().all()
#     )

#     packed_count = sum(
#         1
#         for order in orders
#         if order.order_status == "PACKED"
#     )

#     ready_count = sum(
#         1
#         for order in orders
#         if order.order_status
#         == "READY_FOR_PICKUP"
#     )

#     return templates.TemplateResponse(
#         request=request,

#         name=(
#             "admin/"
#             "delivery_assignments/"
#             "ready_orders.html"
#         ),

#         context={
#             "current_admin":
#                 current_admin,

#             "orders":
#                 orders,

#             "total_orders":
#                 len(orders),

#             "packed_count":
#                 packed_count,

#             "ready_count":
#                 ready_count,

#             "page_title":
#                 "Ready for Delivery",

#             "active_menu":
#                 "delivery_assignments",
                
#                 "active_page": (
#                                                 "Ready_orders"
#                                             ),
                
#                 "partner_options":
#     partner_options,
#         },
#     )
    
    


# # ============================================================
# # ASSIGN DELIVERY PARTNER PAGE
# # ============================================================

# @router.get(
#     "/{order_id}/assign"
# )
# async def assign_delivery_partner_page(
#     order_id: int,

#     request: Request,

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

#     # ========================================================
#     # LOAD ORDER
#     # ========================================================

#     order = (
#         await DeliveryAssignmentService
#         .get_order(
#             db=db,
#             order_id=order_id,
#         )
#     )

#     # ========================================================
#     # VALIDATE ORDER STATUS
#     # ========================================================

#     allowed_statuses = {
#         "PACKED",
#         "READY_FOR_PICKUP",
#     }

#     if order.order_status not in allowed_statuses:

#         return RedirectResponse(
#             url=(
#                 "/admin/delivery-assignments/ready"
#                 "?error=order_not_assignable"
#             ),
#             status_code=303,
#         )

#     # ========================================================
#     # AVAILABLE PARTNERS
#     # ========================================================

#     partners = (
#         await DeliveryAssignmentService
#         .get_available_partners(
#             db=db,
#         )
#     )

#     # ========================================================
#     # BUILD UI DATA
#     # ========================================================

#     partner_rows = []

#     for partner in partners:

#         profile = (
#             partner.delivery_profile
#         )

#         active_delivery_count = (
#             await DeliveryAssignmentService
#             .get_active_delivery_count(
#                 db=db,
#                 partner_id=partner.id,
#             )
#         )

#         partner_rows.append(
#             {
#                 "partner":
#                     partner,

#                 "profile":
#                     profile,

#                 "active_delivery_count":
#                     active_delivery_count,
#             }
#         )

#     # Prefer partners with lower workload first.
#     partner_rows.sort(
#         key=lambda item: (
#             item[
#                 "active_delivery_count"
#             ],
#             item[
#                 "partner"
#             ].full_name.lower(),
#         )
#     )

#     return templates.TemplateResponse(
#         request=request,

#         name=(
#             "admin/"
#             "delivery_assignments/"
#             "assign.html"
#         ),

#         context={
#             "current_admin":
#                 current_admin,

#             "order":
#                 order,

#             "partner_rows":
#                 partner_rows,

#             "page_title":
#                 "Assign Delivery Partner",

#             "active_menu":
#                 "delivery_assignments",
                
#                 "active_page": (
#                                                                 "Ready_orders"
#                                                             ),
#         },
#     )
    
    


# # ============================================================
# # ASSIGN DELIVERY PARTNER
# # ============================================================

# @router.post(
#     "/{order_id}/assign"
# )
# async def assign_delivery_partner_submit(
#     order_id: int,

#     delivery_partner_id: int = Form(...),

#     delivery_note: str = Form(""),

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

#     try:

#         assignment = (
#             await DeliveryAssignmentService
#             .assign_order(
#                 db=db,

#                 order_id=order_id,

#                 partner_id=(
#                     delivery_partner_id
#                 ),

#                 admin_user=(
#                     current_admin
#                 ),

#                 delivery_note=(
#                     delivery_note.strip()
#                     if delivery_note.strip()
#                     else None
#                 ),
#             )
#         )

#         return RedirectResponse(
#             url=(
#                 "/admin/delivery-assignments/ready"
#                 "?assigned=1"
#                 f"&order_id={order_id}"
#                 f"&assignment_id={assignment.id}"
#             ),
#             status_code=303,
#         )

#     except HTTPException as exc:

#         # Service already contains the real
#         # business validation messages.
#         error_message = str(
#             exc.detail
#         )

#     except Exception:

#         error_message = (
#             "Unable to assign delivery partner."
#         )

#     return RedirectResponse(
#         url=(
#             f"/admin/delivery-assignments/"
#             f"{order_id}/assign"
#             "?error="
#             + error_message.replace(
#                 " ",
#                 "%20",
#             )
#         ),
#         status_code=303,
#     )
    





# # ============================================================
# # ORDER DELIVERY ASSIGNMENT HISTORY
# # ============================================================

# @router.get(
#     "/order/{order_id}"
# )
# async def delivery_assignment_history(
#     order_id: int,

#     request: Request,

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

#     # ========================================================
#     # LOAD ORDER + ASSIGNMENTS
#     # ========================================================

#     order = (
#         await DeliveryAssignmentService
#         .get_order(
#             db=db,
#             order_id=order_id,
#         )
#     )

#     assignments = list(
#         order.delivery_assignments
#     )

#     # Oldest assignment first.
#     # assignments.sort(
#     #     key=lambda assignment: (
#     #         assignment.assigned_at,
#     #         assignment.id,
#     #     )
#     # )
#     assignments.sort(
#     key=lambda assignment: (
#         assignment.assigned_at
#         or datetime.min.replace(
#             tzinfo=timezone.utc
#         ),
#         assignment.id,
#     )
# )
#     # ========================================================
#     # LOAD ALL DELIVERY PARTNERS USED BY THIS ORDER
#     # ========================================================

#     partner_ids = {
#         assignment.delivery_partner_id
#         for assignment in assignments
#         if assignment.delivery_partner_id
#         is not None
#     }

#     partner_map = {}

#     if partner_ids:

#         result = await db.execute(
#             select(User)
#             .where(
#                 User.id.in_(
#                     partner_ids
#                 )
#             )
#         )

#         partners = list(
#             result.scalars().all()
#         )

#         partner_map = {
#             partner.id: partner
#             for partner in partners
#         }

#     # ========================================================
#     # BUILD HISTORY ROWS
#     # ========================================================

#     assignment_rows = []

#     active_statuses = {
#         "ASSIGNED",
#         "ACCEPTED",
#         "PICKED_UP",
#         "OUT_FOR_DELIVERY",
#     }

#     for assignment in assignments:

#         partner = partner_map.get(
#             assignment.delivery_partner_id
#         )

#         assignment_rows.append(
#             {
#                 "assignment":
#                     assignment,

#                 "partner":
#                     partner,

#                 "is_active":
#                     assignment.status
#                     in active_statuses,
#             }
#         )

#     current_assignment = next(
#         (
#             row
#             for row in reversed(
#                 assignment_rows
#             )
#             if row["is_active"]
#         ),
#         None,
#     )

#     return templates.TemplateResponse(
#         request=request,

#         name=(
#             "admin/"
#             "delivery_assignments/"
#             "detail.html"
#         ),

#         context={
#             "current_admin":
#                 current_admin,

#             "order":
#                 order,

#             "assignment_rows":
#                 assignment_rows,

#             "current_assignment":
#                 current_assignment,

#             "assignment_count":
#                 len(
#                     assignment_rows
#                 ),

#             "page_title":
#                 "Delivery Assignment Details",

#             "active_menu":
#                 "delivery_assignments",
                
#                 "active_page": (
#                                                                 "Ready_orders"
#                                                             ),
#         },
#     )
    
    




# # ============================================================
# # ACTIVE DELIVERY MONITORING
# # ============================================================

# @router.get("/active")
# async def active_delivery_monitoring(
#     request: Request,

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

#     # ========================================================
#     # LOAD ACTIVE ASSIGNMENTS
#     # ========================================================

#     result = await db.execute(
#         select(
#             DeliveryAssignment,
#             Order,
#             User,
#             DeliveryPartnerProfile,
#         )
#         .join(
#             Order,
#             Order.id
#             == DeliveryAssignment.order_id,
#         )
#         .join(
#             User,
#             User.id
#             == DeliveryAssignment.delivery_partner_id,
#         )
#         .outerjoin(
#             DeliveryPartnerProfile,
#             DeliveryPartnerProfile.user_id
#             == User.id,
#         )
#         .where(
#             DeliveryAssignment.status.in_(
#                 ACTIVE_DELIVERY_STATUSES
#             )
#         )
#         .order_by(
#             DeliveryAssignment.assigned_at.asc(),
#             DeliveryAssignment.id.asc(),
#         )
#     )

#     records = result.all()

#     # ========================================================
#     # PARTNER WORKLOAD
#     # ========================================================

#     workload = Counter(
#         assignment.delivery_partner_id
#         for (
#             assignment,
#             order,
#             partner,
#             profile,
#         ) in records
#     )

#     # ========================================================
#     # BUILD DISPLAY ROWS
#     # ========================================================

#     now = datetime.now(
#         timezone.utc
#     )

#     delivery_rows = []

#     for (
#         assignment,
#         order,
#         partner,
#         profile,
#     ) in records:

#         assigned_at = (
#             assignment.assigned_at
#         )

#         assignment_age_minutes = None

#         if assigned_at:

#             if (
#                 assigned_at.tzinfo
#                 is None
#             ):
#                 assigned_at = (
#                     assigned_at.replace(
#                         tzinfo=timezone.utc
#                     )
#                 )

#             assignment_age_minutes = max(
#                 0,
#                 int(
#                     (
#                         now
#                         - assigned_at
#                     ).total_seconds()
#                     // 60
#                 ),
#             )

#         delivery_rows.append(
#             {
#                 "assignment":
#                     assignment,

#                 "order":
#                     order,

#                 "partner":
#                     partner,

#                 "profile":
#                     profile,

#                 "active_delivery_count":
#                     workload.get(
#                         partner.id,
#                         0,
#                     ),

#                 "assignment_age_minutes":
#                     assignment_age_minutes,
#             }
#         )

#     # ========================================================
#     # SUMMARY COUNTS
#     # ========================================================

#     status_counts = Counter(
#         assignment.status
#         for (
#             assignment,
#             order,
#             partner,
#             profile,
#         ) in records
#     )

#     unique_partner_count = len(
#         {
#             assignment.delivery_partner_id
#             for (
#                 assignment,
#                 order,
#                 partner,
#                 profile,
#             ) in records
#         }
#     )

#     return templates.TemplateResponse(
#         request=request,

#         name=(
#             "admin/"
#             "delivery_assignments/"
#             "active.html"
#         ),

#         context={
#             "current_admin":
#                 current_admin,

#             "delivery_rows":
#                 delivery_rows,

#             "total_active":
#                 len(delivery_rows),

#             "assigned_count":
#                 status_counts.get(
#                     "ASSIGNED",
#                     0,
#                 ),

#             "accepted_count":
#                 status_counts.get(
#                     "ACCEPTED",
#                     0,
#                 ),

#             "picked_up_count":
#                 status_counts.get(
#                     "PICKED_UP",
#                     0,
#                 ),

#             "out_for_delivery_count":
#                 status_counts.get(
#                     "OUT_FOR_DELIVERY",
#                     0,
#                 ),

#             "unique_partner_count":
#                 unique_partner_count,

#             "page_title":
#                 "Active Deliveries",

#             "active_menu":
#                 "active_deliveries",
                
                
#                 "active_page": (
#                                                                 "active_orders"
#                                                             ),
#         },
#     )
    
    




# # ============================================================
# # DELIVERY HISTORY
# # ============================================================

# @router.get("/history")
# async def delivery_history(
#     request: Request,

#     status_filter: str | None = None,
#     search: str | None = None,

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

#     # --------------------------------------------------------
#     # NORMALIZE FILTERS
#     # --------------------------------------------------------

#     selected_status = (
#         status_filter.strip().upper()
#         if status_filter
#         else ""
#     )

#     search_value = (
#         search.strip()
#         if search
#         else ""
#     )

#     # --------------------------------------------------------
#     # BASE QUERY
#     # --------------------------------------------------------

#     query = (
#         select(
#             DeliveryAssignment,
#             Order,
#             User,
#         )
#         .join(
#             Order,
#             Order.id
#             == DeliveryAssignment.order_id,
#         )
#         .join(
#             User,
#             User.id
#             == DeliveryAssignment.delivery_partner_id,
#         )
#         .where(
#             DeliveryAssignment.status.in_(
#                 TERMINAL_DELIVERY_STATUSES
#             )
#         )
#     )

#     # --------------------------------------------------------
#     # STATUS FILTER
#     # --------------------------------------------------------

#     if (
#         selected_status
#         and selected_status
#         in TERMINAL_DELIVERY_STATUSES
#     ):
#         query = query.where(
#             DeliveryAssignment.status
#             == selected_status
#         )

#     # --------------------------------------------------------
#     # SEARCH
#     # --------------------------------------------------------

#     if search_value:

#         pattern = f"%{search_value}%"

#         query = query.where(
#             or_(
#                 Order.order_number.ilike(
#                     pattern
#                 ),

#                 Order.delivery_full_name.ilike(
#                     pattern
#                 ),

#                 Order.delivery_phone.ilike(
#                     pattern
#                 ),

#                 User.full_name.ilike(
#                     pattern
#                 ),

#                 User.phone.ilike(
#                     pattern
#                 ),
#             )
#         )

#     # --------------------------------------------------------
#     # SORT
#     # --------------------------------------------------------

#     query = query.order_by(
#         DeliveryAssignment.id.desc()
#     )

#     result = await db.execute(
#         query
#     )

#     records = result.all()

#     # --------------------------------------------------------
#     # BUILD DISPLAY ROWS
#     # --------------------------------------------------------

#     history_rows = []

#     for (
#         assignment,
#         order,
#         partner,
#     ) in records:

#         completed_at = None

#         if assignment.status == "DELIVERED":
#             completed_at = (
#                 assignment.delivered_at
#             )

#         elif assignment.status == "REJECTED":
#             completed_at = (
#                 assignment.rejected_at
#             )

#         elif assignment.status == "FAILED":
#             completed_at = (
#                 assignment.failed_at
#             )

#         elif assignment.status == "CANCELLED":
#             completed_at = (
#                 assignment.cancelled_at
#             )

#         history_rows.append(
#             {
#                 "assignment":
#                     assignment,

#                 "order":
#                     order,

#                 "partner":
#                     partner,

#                 "completed_at":
#                     completed_at,
#             }
#         )

#     # --------------------------------------------------------
#     # SUMMARY COUNTS
#     # --------------------------------------------------------

#     count_result = await db.execute(
#         select(
#             DeliveryAssignment.status,
#             func.count(
#                 DeliveryAssignment.id
#             ),
#         )
#         .where(
#             DeliveryAssignment.status.in_(
#                 TERMINAL_DELIVERY_STATUSES
#             )
#         )
#         .group_by(
#             DeliveryAssignment.status
#         )
#     )

#     status_counts = {
#         row[0]: row[1]
#         for row in count_result.all()
#     }

#     delivered_count = (
#         status_counts.get(
#             "DELIVERED",
#             0,
#         )
#     )

#     rejected_count = (
#         status_counts.get(
#             "REJECTED",
#             0,
#         )
#     )

#     failed_count = (
#         status_counts.get(
#             "FAILED",
#             0,
#         )
#     )

#     cancelled_count = (
#         status_counts.get(
#             "CANCELLED",
#             0,
#         )
#     )

#     total_history = (
#         delivered_count
#         + rejected_count
#         + failed_count
#         + cancelled_count
#     )

#     return templates.TemplateResponse(
#         request=request,

#         name=(
#             "admin/"
#             "delivery_assignments/"
#             "history.html"
#         ),

#         context={
#             "current_admin":
#                 current_admin,

#             "history_rows":
#                 history_rows,

#             "selected_status":
#                 selected_status,

#             "search_value":
#                 search_value,

#             "total_history":
#                 total_history,

#             "delivered_count":
#                 delivered_count,

#             "rejected_count":
#                 rejected_count,

#             "failed_count":
#                 failed_count,

#             "cancelled_count":
#                 cancelled_count,

#             "page_title":
#                 "Delivery History",

#             "active_menu":
#                 "delivery_history",
                
#                 "active_page": (
#                                                                                 "history"
#                                                                             ),
#         },
#     )
    
    




# # ============================================================
# # DELIVERY MAP
# # ============================================================

# @router.get("/map")
# async def delivery_map(
#     request: Request,

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

#     # ========================================================
#     # LOAD ACTIVE DELIVERY ASSIGNMENTS
#     # ========================================================

#     result = await db.execute(
#         select(
#             DeliveryAssignment,
#             Order,
#             User,
#             DeliveryPartnerProfile,
#         )
#         .join(
#             Order,
#             Order.id
#             == DeliveryAssignment.order_id,
#         )
#         .join(
#             User,
#             User.id
#             == DeliveryAssignment.delivery_partner_id,
#         )
#         .outerjoin(
#             DeliveryPartnerProfile,
#             DeliveryPartnerProfile.user_id
#             == User.id,
#         )
#         .where(
#             DeliveryAssignment.status.in_(
#                 ACTIVE_DELIVERY_STATUSES
#             )
#         )
#         .order_by(
#             User.full_name.asc(),
#             DeliveryAssignment.assigned_at.asc(),
#         )
#     )

#     records = result.all()

#     # ========================================================
#     # GROUP ACTIVE ORDERS BY DELIVERY PARTNER
#     # ========================================================

#     partner_map_data = {}

#     for (
#         assignment,
#         order,
#         partner,
#         profile,
#     ) in records:

#         # Partner must have reported GPS location.
#         if (
#             profile is None
#             or profile.current_latitude is None
#             or profile.current_longitude is None
#         ):
#             continue

#         partner_id = partner.id

#         if partner_id not in partner_map_data:

#             # ------------------------------------------------
#             # LOCATION AGE
#             # ------------------------------------------------

#             location_age_minutes = None

#             if profile.last_location_at:

#                 last_location_at = (
#                     profile.last_location_at
#                 )

#                 if last_location_at.tzinfo is None:
#                     last_location_at = (
#                         last_location_at.replace(
#                             tzinfo=timezone.utc
#                         )
#                     )

#                 location_age_minutes = max(
#                     0,
#                     int(
#                         (
#                             datetime.now(
#                                 timezone.utc
#                             )
#                             - last_location_at
#                         ).total_seconds()
#                         // 60
#                     ),
#                 )

#             partner_map_data[
#                 partner_id
#             ] = {
#                 "partner_id":
#                     partner.id,

#                 "name":
#                     partner.full_name,

#                 "phone":
#                     partner.phone,

#                 "vehicle_type":
#                     profile.vehicle_type,

#                 "vehicle_number":
#                     profile.vehicle_number,

#                 "is_online":
#                     bool(
#                         profile.is_online
#                     ),

#                 "latitude":
#                     float(
#                         profile.current_latitude
#                     ),

#                 "longitude":
#                     float(
#                         profile.current_longitude
#                     ),

#                 "last_location_at":
#                     (
#                         profile.last_location_at.isoformat()
#                         if profile.last_location_at
#                         else None
#                     ),

#                 "location_age_minutes":
#                     location_age_minutes,

#                 "orders":
#                     [],
#             }

#         # ====================================================
#         # ACTIVE ORDER DETAILS
#         # ====================================================

#         order_data = {
#             "order_id":
#                 order.id,

#             "order_number":
#                 order.order_number,

#             "status":
#                 assignment.status,

#             "customer":
#                 order.delivery_full_name,

#             "customer_phone":
#                 order.delivery_phone,

#             "village_town":
#                 order.delivery_village_town,

#             "district":
#                 order.delivery_district,

#             "total_amount":
#                 float(
#                     order.total_amount
#                 ),

#             "customer_latitude":
#                 (
#                     float(
#                         order.delivery_latitude
#                     )
#                     if order.delivery_latitude
#                     is not None
#                     else None
#                 ),

#             "customer_longitude":
#                 (
#                     float(
#                         order.delivery_longitude
#                     )
#                     if order.delivery_longitude
#                     is not None
#                     else None
#                 ),
#         }

#         partner_map_data[
#             partner_id
#         ]["orders"].append(
#             order_data
#         )

#     # ========================================================
#     # FINAL SERIALIZABLE LIST
#     # ========================================================

#     map_partners = list(
#         partner_map_data.values()
#     )

#     partners_with_location = len(
#         map_partners
#     )

#     active_orders_on_map = sum(
#         len(
#             partner["orders"]
#         )
#         for partner in map_partners
#     )

#     # Active partners that have assignments
#     # but no GPS location yet.
#     active_partner_ids = {
#         assignment.delivery_partner_id
#         for (
#             assignment,
#             order,
#             partner,
#             profile,
#         ) in records
#     }

#     missing_location_count = (
#         len(active_partner_ids)
#         - partners_with_location
#     )

#     return templates.TemplateResponse(
#         request=request,

#         name=(
#             "admin/"
#             "delivery_assignments/"
#             "map.html"
#         ),

#         context={
#             "current_admin":
#                 current_admin,

#             "map_partners":
#                 map_partners,

#             "partners_with_location":
#                 partners_with_location,

#             "missing_location_count":
#                 missing_location_count,

#             "active_orders_on_map":
#                 active_orders_on_map,

#             "total_active_partners":
#                 len(
#                     active_partner_ids
#                 ),

#             "page_title":
#                 "Delivery Map",

#             "active_menu":
#                 "delivery_map",
                
#                  "active_page": (
#                                                                                                 "map"
#                                                                                             ),
#         },
#     )
    
    





# @router.post(
#     "/bulk-assign",
#     dependencies=[
#         Depends(get_admin_web_user)
#     ],
# )
# async def bulk_assign_orders(
#     request: Request,

#     order_ids: list[int] = Form(
#         default=[]
#     ),

#     delivery_partner_id: int = Form(...),

#     delivery_note: str | None = Form(
#         default=None
#     ),

#     current_admin: User = Depends(
#         get_admin_web_user
#     ),

#     db: AsyncSession = Depends(
#         get_db
#     ),
# ):

#     if not order_ids:

#         flash(
#             request,
#             "Please select at least one order.",
#             "warning",
#         )

#         return RedirectResponse(
#             url=(
#                 "/admin/"
#                 "delivery-assignments/"
#                 "ready"
#             ),
#             status_code=303,
#         )

#     # --------------------------------------------------------
#     # VALIDATE PARTNER ONCE
#     # --------------------------------------------------------

#     partner = (
#         await DeliveryAssignmentService
#         .get_delivery_partner(
#             db,
#             delivery_partner_id,
#         )
#     )

#     profile = (
#         partner.delivery_profile
#     )

#     if (
#         profile is None
#         or not partner.is_active
#         or not profile.is_approved
#         or not profile.is_online
#     ):

#         flash(
#             request,
#             (
#                 "Selected delivery partner "
#                 "is not currently assignable."
#             ),
#             "danger",
#         )

#         return RedirectResponse(
#             url=(
#                 "/admin/"
#                 "delivery-assignments/"
#                 "ready"
#             ),
#             status_code=303,
#         )

#     assigned_count = 0
#     skipped_count = 0
#     failed_count = 0

#     # Remove accidental duplicate IDs.
#     unique_order_ids = list(
#         dict.fromkeys(
#             order_ids
#         )
#     )

#     for order_id in unique_order_ids:

#         try:

#             order = (
#                 await DeliveryAssignmentService
#                 .get_order(
#                     db,
#                     order_id,
#                 )
#             )

#             if order.order_status not in {
#                 "PACKED",
#                 "READY_FOR_PICKUP",
#             }:

#                 skipped_count += 1
#                 continue

#             await DeliveryAssignmentService.assign_order(
#                 db=db,
#                 order_id=order.id,
#                 partner_id=delivery_partner_id,
#                 admin_user=current_admin,
#                 delivery_note=delivery_note,
#             )

#             assigned_count += 1

#         except HTTPException:

#             failed_count += 1

#         except Exception:

#             failed_count += 1

#     # --------------------------------------------------------
#     # FLASH RESULT
#     # --------------------------------------------------------

#     if assigned_count > 0:

#         message = (
#             f"{assigned_count} order"
#             f"{'s' if assigned_count != 1 else ''} "
#             f"assigned successfully to "
#             f"{partner.full_name}."
#         )

#         if skipped_count:

#             message += (
#                 f" {skipped_count} order"
#                 f"{'s were' if skipped_count != 1 else ' was'} "
#                 f"skipped because "
#                 f"{'they were' if skipped_count != 1 else 'it was'} "
#                 f"no longer ready for assignment."
#             )

#         if failed_count:

#             message += (
#                 f" {failed_count} order"
#                 f"{'s' if failed_count != 1 else ''} "
#                 f"could not be assigned."
#             )

#         flash(
#             request,
#             message,
#             "success",
#         )

#     else:

#         flash(
#             request,
#             (
#                 "No selected orders could "
#                 "be assigned."
#             ),
#             "warning",
#         )

#     return RedirectResponse(
#         url=(
#             "/admin/"
#             "delivery-assignments/"
#             "ready"
#         ),
#         status_code=303,
#     )
    
    
    




# from fastapi import (
#     APIRouter,
#     Depends,
#     Request,
# )

# from sqlalchemy import (
#     select,
# )

# from sqlalchemy.ext.asyncio import (
#     AsyncSession,
# )

# from app.db.session import (
#     get_db,
# )

# from app.models.order import (
#     Order,
# )

# from app.models.user import (
#     User,
# )

# from app.web.dependencies import (
#     get_admin_web_user,
# )

# from app.web.templates import (
#     templates,
# )


# from curses import flash

from app.models.delivery_assignment import (
    DeliveryAssignment,
)

from app.models.delivery_partner import (
    DeliveryPartnerProfile,
)

from app.models.order import Order
from app.models.user import User

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
)

from fastapi.responses import (
    RedirectResponse,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.models.order import Order
from app.models.user import User

from app.services.delivery_assignment_service import (
    DeliveryAssignmentService,
)


from sqlalchemy import (
    func,
    or_,
    select,
)


from app.web.dependencies import (
    get_admin_web_user,
)

from app.web.templates import templates
from app.web.flash import flash
from app.web.csrf import validate_csrf


from sqlalchemy import (
    select,
)

from app.models.user import User

from app.services.delivery_assignment_service import (
    DeliveryAssignmentService,
)



from collections import Counter
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery_assignment import (
    DeliveryAssignment,
)

from app.models.delivery_partner import (
    DeliveryPartnerProfile,
)

from app.models.order import Order
from app.models.user import User

ACTIVE_DELIVERY_STATUSES = {
    "ASSIGNED",
    "ACCEPTED",
    "PICKED_UP",
    "OUT_FOR_DELIVERY",
}

TERMINAL_DELIVERY_STATUSES = {
    "DELIVERED",
    "REJECTED",
    "FAILED",
    "CANCELLED",
}



router = APIRouter(
    prefix="/delivery-assignments",
)


# ============================================================
# READY FOR DELIVERY ORDERS
# ============================================================

@router.get("/ready")
async def ready_for_delivery_orders(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):
    
    
    partners = (
    await DeliveryAssignmentService
    .get_available_partners(
        db
    )
)
    
    
    

    partner_options = []

    for partner in partners:

        active_count = (
            await DeliveryAssignmentService
            .get_active_delivery_count(
                db,
                partner.id,
            )
        )

        partner_options.append(
            {
                "partner":
                    partner,

                "active_count":
                    active_count,
            }
        )
        
        
    
    partner_options.sort(
    key=lambda item: (
        item["active_count"],
        item["partner"].full_name.lower(),
    )
)

    result = await db.execute(
        select(Order)
        .where(
            Order.order_status.in_(
                [
                    "PACKED",
                    "READY_FOR_PICKUP",
                ]
            )
        )
        .order_by(
            Order.created_at.asc()
        )
    )

    orders = list(
        result.scalars().all()
    )

    packed_count = sum(
        1
        for order in orders
        if order.order_status == "PACKED"
    )

    ready_count = sum(
        1
        for order in orders
        if order.order_status
        == "READY_FOR_PICKUP"
    )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/"
            "delivery_assignments/"
            "ready_orders.html"
        ),

        context={
            "current_admin":
                current_admin,

            "orders":
                orders,

            "total_orders":
                len(orders),

            "packed_count":
                packed_count,

            "ready_count":
                ready_count,

            "page_title":
                "Ready for Delivery",

            "active_menu":
                "delivery_assignments",
                
                "active_page": (
                                                "Ready_orders"
                                            ),
                
                "partner_options":
    partner_options,
        },
    )
    
    


# ============================================================
# ASSIGN DELIVERY PARTNER PAGE
# ============================================================

@router.get(
    "/{order_id}/assign"
)
async def assign_delivery_partner_page(
    order_id: int,

    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    # ========================================================
    # LOAD ORDER
    # ========================================================

    order = (
        await DeliveryAssignmentService
        .get_order(
            db=db,
            order_id=order_id,
        )
    )

    # ========================================================
    # VALIDATE ORDER STATUS
    # ========================================================

    allowed_statuses = {
        "PACKED",
        "READY_FOR_PICKUP",
    }

    if order.order_status not in allowed_statuses:

        return RedirectResponse(
            url=(
                "/admin/delivery-assignments/ready"
                "?error=order_not_assignable"
            ),
            status_code=303,
        )

    # ========================================================
    # AVAILABLE PARTNERS
    # ========================================================

    partners = (
        await DeliveryAssignmentService
        .get_available_partners(
            db=db,
        )
    )

    # ========================================================
    # BUILD UI DATA
    # ========================================================

    partner_rows = []

    for partner in partners:

        profile = (
            partner.delivery_profile
        )

        active_delivery_count = (
            await DeliveryAssignmentService
            .get_active_delivery_count(
                db=db,
                partner_id=partner.id,
            )
        )

        partner_rows.append(
            {
                "partner":
                    partner,

                "profile":
                    profile,

                "active_delivery_count":
                    active_delivery_count,
            }
        )

    # Prefer partners with lower workload first.
    partner_rows.sort(
        key=lambda item: (
            item[
                "active_delivery_count"
            ],
            item[
                "partner"
            ].full_name.lower(),
        )
    )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/"
            "delivery_assignments/"
            "assign.html"
        ),

        context={
            "current_admin":
                current_admin,

            "order":
                order,

            "partner_rows":
                partner_rows,

            "page_title":
                "Assign Delivery Partner",

            "active_menu":
                "delivery_assignments",
                
                "active_page": (
                                                                "Ready_orders"
                                                            ),
        },
    )
    
    


# ============================================================
# ASSIGN DELIVERY PARTNER
# ============================================================

@router.post(
    "/{order_id}/assign"
)
async def assign_delivery_partner_submit(
    order_id: int,

    delivery_partner_id: int = Form(...),

    delivery_note: str = Form(""),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    try:

        assignment = (
            await DeliveryAssignmentService
            .assign_order(
                db=db,

                order_id=order_id,

                partner_id=(
                    delivery_partner_id
                ),

                admin_user=(
                    current_admin
                ),

                delivery_note=(
                    delivery_note.strip()
                    if delivery_note.strip()
                    else None
                ),
            )
        )

        return RedirectResponse(
            url=(
                "/admin/delivery-assignments/ready"
                "?assigned=1"
                f"&order_id={order_id}"
                f"&assignment_id={assignment.id}"
            ),
            status_code=303,
        )

    except HTTPException as exc:

        # Service already contains the real
        # business validation messages.
        error_message = str(
            exc.detail
        )

    except Exception:

        error_message = (
            "Unable to assign delivery partner."
        )

    return RedirectResponse(
        url=(
            f"/admin/delivery-assignments/"
            f"{order_id}/assign"
            "?error="
            + error_message.replace(
                " ",
                "%20",
            )
        ),
        status_code=303,
    )
    





# ============================================================
# ORDER DELIVERY ASSIGNMENT HISTORY
# ============================================================

@router.get(
    "/order/{order_id}"
)
async def delivery_assignment_history(
    order_id: int,

    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    # ========================================================
    # LOAD ORDER + ASSIGNMENTS
    # ========================================================

    order = (
        await DeliveryAssignmentService
        .get_order(
            db=db,
            order_id=order_id,
        )
    )

    assignments = list(
        order.delivery_assignments
    )

    # Oldest assignment first.
    # assignments.sort(
    #     key=lambda assignment: (
    #         assignment.assigned_at,
    #         assignment.id,
    #     )
    # )
    assignments.sort(
    key=lambda assignment: (
        assignment.assigned_at
        or datetime.min.replace(
            tzinfo=timezone.utc
        ),
        assignment.id,
    )
)
    # ========================================================
    # LOAD ALL DELIVERY PARTNERS USED BY THIS ORDER
    # ========================================================

    partner_ids = {
        assignment.delivery_partner_id
        for assignment in assignments
        if assignment.delivery_partner_id
        is not None
    }

    partner_map = {}

    if partner_ids:

        result = await db.execute(
            select(User)
            .where(
                User.id.in_(
                    partner_ids
                )
            )
        )

        partners = list(
            result.scalars().all()
        )

        partner_map = {
            partner.id: partner
            for partner in partners
        }

    # ========================================================
    # BUILD HISTORY ROWS
    # ========================================================

    assignment_rows = []

    active_statuses = {
        "ASSIGNED",
        "ACCEPTED",
        "PICKED_UP",
        "OUT_FOR_DELIVERY",
    }

    for assignment in assignments:

        partner = partner_map.get(
            assignment.delivery_partner_id
        )

        assignment_rows.append(
            {
                "assignment":
                    assignment,

                "partner":
                    partner,

                "is_active":
                    assignment.status
                    in active_statuses,
            }
        )

    current_assignment = next(
        (
            row
            for row in reversed(
                assignment_rows
            )
            if row["is_active"]
        ),
        None,
    )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/"
            "delivery_assignments/"
            "detail.html"
        ),

        context={
            "current_admin":
                current_admin,

            "order":
                order,

            "assignment_rows":
                assignment_rows,

            "current_assignment":
                current_assignment,

            "assignment_count":
                len(
                    assignment_rows
                ),

            "page_title":
                "Delivery Assignment Details",

            "active_menu":
                "delivery_assignments",
                
                "active_page": (
                                                                "Ready_orders"
                                                            ),
        },
    )
    
    




# ============================================================
# ACTIVE DELIVERY MONITORING
# ============================================================

@router.get("/active")
async def active_delivery_monitoring(
    request: Request,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    # ========================================================
    # LOAD ACTIVE ASSIGNMENTS
    # ========================================================

    result = await db.execute(
        select(
            DeliveryAssignment,
            Order,
            User,
            DeliveryPartnerProfile,
        )
        .join(
            Order,
            Order.id
            == DeliveryAssignment.order_id,
        )
        .join(
            User,
            User.id
            == DeliveryAssignment.delivery_partner_id,
        )
        .outerjoin(
            DeliveryPartnerProfile,
            DeliveryPartnerProfile.user_id
            == User.id,
        )
        .where(
            DeliveryAssignment.status.in_(
                ACTIVE_DELIVERY_STATUSES
            )
        )
        .order_by(
            DeliveryAssignment.assigned_at.asc(),
            DeliveryAssignment.id.asc(),
        )
    )

    records = result.all()

    # ========================================================
    # PARTNER WORKLOAD
    # ========================================================

    workload = Counter(
        assignment.delivery_partner_id
        for (
            assignment,
            order,
            partner,
            profile,
        ) in records
    )

    # ========================================================
    # BUILD DISPLAY ROWS
    # ========================================================

    now = datetime.now(
        timezone.utc
    )

    delivery_rows = []

    for (
        assignment,
        order,
        partner,
        profile,
    ) in records:

        assigned_at = (
            assignment.assigned_at
        )

        assignment_age_minutes = None

        if assigned_at:

            if (
                assigned_at.tzinfo
                is None
            ):
                assigned_at = (
                    assigned_at.replace(
                        tzinfo=timezone.utc
                    )
                )

            assignment_age_minutes = max(
                0,
                int(
                    (
                        now
                        - assigned_at
                    ).total_seconds()
                    // 60
                ),
            )

        delivery_rows.append(
            {
                "assignment":
                    assignment,

                "order":
                    order,

                "partner":
                    partner,

                "profile":
                    profile,

                "active_delivery_count":
                    workload.get(
                        partner.id,
                        0,
                    ),

                "assignment_age_minutes":
                    assignment_age_minutes,
            }
        )

    # ========================================================
    # SUMMARY COUNTS
    # ========================================================

    status_counts = Counter(
        assignment.status
        for (
            assignment,
            order,
            partner,
            profile,
        ) in records
    )

    unique_partner_count = len(
        {
            assignment.delivery_partner_id
            for (
                assignment,
                order,
                partner,
                profile,
            ) in records
        }
    )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/"
            "delivery_assignments/"
            "active.html"
        ),

        context={
            "current_admin":
                current_admin,

            "delivery_rows":
                delivery_rows,

            "total_active":
                len(delivery_rows),

            "assigned_count":
                status_counts.get(
                    "ASSIGNED",
                    0,
                ),

            "accepted_count":
                status_counts.get(
                    "ACCEPTED",
                    0,
                ),

            "picked_up_count":
                status_counts.get(
                    "PICKED_UP",
                    0,
                ),

            "out_for_delivery_count":
                status_counts.get(
                    "OUT_FOR_DELIVERY",
                    0,
                ),

            "unique_partner_count":
                unique_partner_count,

            "page_title":
                "Active Deliveries",

            "active_menu":
                "active_deliveries",
                
                
                "active_page": (
                                                                "active_orders"
                                                            ),
        },
    )
    
    




# ============================================================
# DELIVERY HISTORY
# ============================================================

@router.get("/history")
async def delivery_history(
    request: Request,

    status_filter: str | None = None,
    search: str | None = None,

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    # --------------------------------------------------------
    # NORMALIZE FILTERS
    # --------------------------------------------------------

    selected_status = (
        status_filter.strip().upper()
        if status_filter
        else ""
    )

    search_value = (
        search.strip()
        if search
        else ""
    )

    # --------------------------------------------------------
    # BASE QUERY
    # --------------------------------------------------------

    query = (
        select(
            DeliveryAssignment,
            Order,
            User,
        )
        .join(
            Order,
            Order.id
            == DeliveryAssignment.order_id,
        )
        .join(
            User,
            User.id
            == DeliveryAssignment.delivery_partner_id,
        )
        .where(
            DeliveryAssignment.status.in_(
                TERMINAL_DELIVERY_STATUSES
            )
        )
    )

    # --------------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------------

    if (
        selected_status
        and selected_status
        in TERMINAL_DELIVERY_STATUSES
    ):
        query = query.where(
            DeliveryAssignment.status
            == selected_status
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search_value:

        pattern = f"%{search_value}%"

        query = query.where(
            or_(
                Order.order_number.ilike(
                    pattern
                ),

                Order.delivery_full_name.ilike(
                    pattern
                ),

                Order.delivery_phone.ilike(
                    pattern
                ),

                User.full_name.ilike(
                    pattern
                ),

                User.phone.ilike(
                    pattern
                ),
            )
        )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    query = query.order_by(
        DeliveryAssignment.id.desc()
    )

    result = await db.execute(
        query
    )

    records = result.all()

    # --------------------------------------------------------
    # BUILD DISPLAY ROWS
    # --------------------------------------------------------

    history_rows = []

    for (
        assignment,
        order,
        partner,
    ) in records:

        completed_at = None

        if assignment.status == "DELIVERED":
            completed_at = (
                assignment.delivered_at
            )

        elif assignment.status == "REJECTED":
            completed_at = (
                assignment.rejected_at
            )

        elif assignment.status == "FAILED":
            completed_at = (
                assignment.failed_at
            )

        elif assignment.status == "CANCELLED":
            completed_at = (
                assignment.cancelled_at
            )

        history_rows.append(
            {
                "assignment":
                    assignment,

                "order":
                    order,

                "partner":
                    partner,

                "completed_at":
                    completed_at,
            }
        )

    # --------------------------------------------------------
    # SUMMARY COUNTS
    # --------------------------------------------------------

    count_result = await db.execute(
        select(
            DeliveryAssignment.status,
            func.count(
                DeliveryAssignment.id
            ),
        )
        .where(
            DeliveryAssignment.status.in_(
                TERMINAL_DELIVERY_STATUSES
            )
        )
        .group_by(
            DeliveryAssignment.status
        )
    )

    status_counts = {
        row[0]: row[1]
        for row in count_result.all()
    }

    delivered_count = (
        status_counts.get(
            "DELIVERED",
            0,
        )
    )

    rejected_count = (
        status_counts.get(
            "REJECTED",
            0,
        )
    )

    failed_count = (
        status_counts.get(
            "FAILED",
            0,
        )
    )

    cancelled_count = (
        status_counts.get(
            "CANCELLED",
            0,
        )
    )

    total_history = (
        delivered_count
        + rejected_count
        + failed_count
        + cancelled_count
    )

    return templates.TemplateResponse(
        request=request,

        name=(
            "admin/"
            "delivery_assignments/"
            "history.html"
        ),

        context={
            "current_admin":
                current_admin,

            "history_rows":
                history_rows,

            "selected_status":
                selected_status,

            "search_value":
                search_value,

            "total_history":
                total_history,

            "delivered_count":
                delivered_count,

            "rejected_count":
                rejected_count,

            "failed_count":
                failed_count,

            "cancelled_count":
                cancelled_count,

            "page_title":
                "Delivery History",

            "active_menu":
                "delivery_history",
                
                "active_page": (
                                                                                "history"
                                                                            ),
        },
    )
    
    




# ============================================================
# DELIVERY MAP
# ============================================================
# BULK ASSIGN DELIVERY PARTNER
# ============================================================

@router.post(
    "/bulk-assign",
    dependencies=[
        Depends(validate_csrf)
    ],
)
async def bulk_assign_orders(
    request: Request,

    order_ids: list[int] = Form(
        default=[]
    ),

    delivery_partner_id: int = Form(...),

    delivery_note: str | None = Form(
        default=None
    ),

    current_admin: User = Depends(
        get_admin_web_user
    ),

    db: AsyncSession = Depends(
        get_db
    ),
):

    # --------------------------------------------------------
    # NOTHING SELECTED
    # --------------------------------------------------------

    if not order_ids:

        flash(
            request,
            "Please select at least one order.",
            "warning",
        )

        return RedirectResponse(
            url="/admin/delivery-assignments/ready",
            status_code=303,
        )

    # Remove accidental duplicate order IDs while
    # preserving the order selected by the admin.
    unique_order_ids = list(
        dict.fromkeys(order_ids)
    )

    # --------------------------------------------------------
    # LOAD + VALIDATE DELIVERY PARTNER
    # --------------------------------------------------------

    try:

        partner = (
            await DeliveryAssignmentService
            .get_delivery_partner(
                db=db,
                partner_id=delivery_partner_id,
            )
        )

    except HTTPException as exc:

        flash(
            request,
            str(exc.detail),
            "danger",
        )

        return RedirectResponse(
            url="/admin/delivery-assignments/ready",
            status_code=303,
        )

    profile = partner.delivery_profile

    if (
        profile is None
        or not partner.is_active
        or not profile.is_approved
        or not profile.is_online
    ):

        flash(
            request,
            (
                "Selected delivery partner is not "
                "currently assignable."
            ),
            "danger",
        )

        return RedirectResponse(
            url="/admin/delivery-assignments/ready",
            status_code=303,
        )

    # --------------------------------------------------------
    # ASSIGN SELECTED ORDERS
    # --------------------------------------------------------

    assigned_count = 0
    skipped_count = 0
    failed_count = 0

    for order_id in unique_order_ids:

        try:

            order = (
                await DeliveryAssignmentService
                .get_order(
                    db=db,
                    order_id=order_id,
                )
            )

            # Re-check on the server because the order status
            # may have changed after the page was opened.
            if order.order_status not in {
                "PACKED",
                "READY_FOR_PICKUP",
            }:

                skipped_count += 1
                continue

            await DeliveryAssignmentService.assign_order(
                db=db,
                order_id=order.id,
                partner_id=partner.id,
                admin_user=current_admin,
                delivery_note=(
                    delivery_note.strip()
                    if delivery_note
                    and delivery_note.strip()
                    else None
                ),
            )

            assigned_count += 1

        except HTTPException:

            # The assignment service contains the real business
            # validations (duplicate active assignment, stale
            # order state, partner state, etc.).
            failed_count += 1

        except Exception:

            # Do not stop the remaining selected orders because
            # one order failed to assign.
            failed_count += 1

    # --------------------------------------------------------
    # RESULT MESSAGE
    # --------------------------------------------------------

    if assigned_count > 0:

        parts = [
            (
                f"{assigned_count} order"
                f"{'s' if assigned_count != 1 else ''} "
                f"assigned successfully to "
                f"{partner.full_name}."
            )
        ]

        if skipped_count:
            parts.append(
                (
                    f"{skipped_count} order"
                    f"{'s were' if skipped_count != 1 else ' was'} "
                    f"skipped because "
                    f"{'they are' if skipped_count != 1 else 'it is'} "
                    f"no longer ready for assignment."
                )
            )

        if failed_count:
            parts.append(
                (
                    f"{failed_count} order"
                    f"{'s' if failed_count != 1 else ''} "
                    f"could not be assigned."
                )
            )

        flash(
            request,
            " ".join(parts),
            "success" if failed_count == 0 else "warning",
        )

    else:

        flash(
            request,
            (
                "No selected orders could be assigned. "
                "Please refresh and try again."
            ),
            "warning",
        )

    return RedirectResponse(
        url="/admin/delivery-assignments/ready",
        status_code=303,
    )

