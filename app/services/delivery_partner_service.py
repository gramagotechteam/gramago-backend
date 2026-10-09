# from sqlalchemy import or_, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.user import User
# from app.models.delivery_partner import DeliveryPartnerProfile

# from app.schemas.delivery_partner import (
#     DeliveryPartnerCreate,
#     DeliveryPartnerUpdate,
# )

# # IMPORTANT:
# # Replace this import with your existing password hashing function.
# from app.core.security import hash_password


# class DeliveryPartnerService:

#     # =========================================================
#     # CREATE DELIVERY PARTNER
#     # =========================================================

#     @staticmethod
#     async def create(
#         db: AsyncSession,
#         data: DeliveryPartnerCreate,
#     ) -> User:

#         # -----------------------------------------------------
#         # Check duplicate phone/email
#         # -----------------------------------------------------

#         conditions = [
#             User.phone == data.phone,
#         ]

#         if data.email:
#             conditions.append(User.email == data.email)

#         result = await db.execute(
#             select(User).where(
#                 or_(*conditions)
#             )
#         )

#         existing_user = result.scalar_one_or_none()

#         if existing_user:
#             if existing_user.phone == data.phone:
#                 raise ValueError(
#                     "A user with this phone number already exists."
#                 )

#             raise ValueError(
#                 "A user with this email already exists."
#             )

#         # -----------------------------------------------------
#         # Create base user
#         # -----------------------------------------------------

#         user = User(
#             full_name=data.full_name.strip(),
#             email=(
#                 str(data.email).lower()
#                 if data.email
#                 else None
#             ),
#             phone=data.phone.strip(),
#             password_hash=hash_password(data.password),

#             role="DELIVERY_PARTNER",

#             # Created by admin, therefore verified internally.
#             is_verified=True,

#             # Can login only if active.
#             is_active=True,
#         )

#         db.add(user)

#         # Get generated user.id
#         await db.flush()

#         # -----------------------------------------------------
#         # Create delivery profile
#         # -----------------------------------------------------

#         profile = DeliveryPartnerProfile(
#             user_id=user.id,

#             vehicle_type=(
#                 data.vehicle_type.strip()
#                 if data.vehicle_type
#                 else None
#             ),

#             vehicle_number=(
#                 data.vehicle_number.strip().upper()
#                 if data.vehicle_number
#                 else None
#             ),

#             is_online=False,
#             is_available=True,

#             # Explicit admin approval can happen afterwards.
#             is_approved=False,
#         )

#         db.add(profile)

#         await db.commit()

#         await db.refresh(user)

#         return user


#     # =========================================================
#     # GET DELIVERY PARTNER
#     # =========================================================

#     @staticmethod
#     async def get_by_id(
#         db: AsyncSession,
#         user_id: int,
#     ) -> User | None:

#         result = await db.execute(
#             select(User)
#             .where(
#                 User.id == user_id,
#                 User.role == "DELIVERY_PARTNER",
#             )
#         )

#         return result.scalar_one_or_none()


#     # =========================================================
#     # LIST DELIVERY PARTNERS
#     # =========================================================

#     @staticmethod
#     async def list_all(
#         db: AsyncSession,
#     ) -> list[User]:

#         result = await db.execute(
#             select(User)
#             .where(
#                 User.role == "DELIVERY_PARTNER"
#             )
#             .order_by(
#                 User.created_at.desc()
#             )
#         )

#         return list(
#             result.scalars().all()
#         )


#     # =========================================================
#     # UPDATE
#     # =========================================================

#     @staticmethod
#     async def update(
#         db: AsyncSession,
#         user: User,
#         data: DeliveryPartnerUpdate,
#     ) -> User:

#         # -----------------------------------------------------
#         # Name
#         # -----------------------------------------------------

#         if data.full_name is not None:
#             user.full_name = data.full_name.strip()

#         # -----------------------------------------------------
#         # Email
#         # -----------------------------------------------------

#         if data.email is not None:

#             email = str(data.email).lower()

#             result = await db.execute(
#                 select(User).where(
#                     User.email == email,
#                     User.id != user.id,
#                 )
#             )

#             if result.scalar_one_or_none():
#                 raise ValueError(
#                     "Another user already uses this email."
#                 )

#             user.email = email

#         # -----------------------------------------------------
#         # Phone
#         # -----------------------------------------------------

#         if data.phone is not None:

#             phone = data.phone.strip()

#             result = await db.execute(
#                 select(User).where(
#                     User.phone == phone,
#                     User.id != user.id,
#                 )
#             )

#             if result.scalar_one_or_none():
#                 raise ValueError(
#                     "Another user already uses this phone number."
#                 )

#             user.phone = phone

#         # -----------------------------------------------------
#         # Delivery profile
#         # -----------------------------------------------------

#         profile = user.delivery_profile

#         if profile is None:
#             raise ValueError(
#                 "Delivery partner profile does not exist."
#             )

#         if data.vehicle_type is not None:
#             profile.vehicle_type = (
#                 data.vehicle_type.strip()
#                 or None
#             )

#         if data.vehicle_number is not None:
#             profile.vehicle_number = (
#                 data.vehicle_number.strip().upper()
#                 or None
#             )

#         await db.commit()
#         await db.refresh(user)

#         return user


#     # =========================================================
#     # APPROVE / UNAPPROVE
#     # =========================================================

#     @staticmethod
#     async def set_approval(
#         db: AsyncSession,
#         user: User,
#         approved: bool,
#     ) -> User:

#         profile = user.delivery_profile

#         if profile is None:
#             raise ValueError(
#                 "Delivery partner profile does not exist."
#             )

#         profile.is_approved = approved

#         # Safety:
#         # immediately take an unapproved partner offline.
#         if not approved:
#             profile.is_online = False
#             profile.is_available = False

#         else:
#             profile.is_available = True

#         await db.commit()
#         await db.refresh(user)

#         return user


#     # =========================================================
#     # ACTIVATE / DEACTIVATE ACCOUNT
#     # =========================================================

#     @staticmethod
#     async def set_active(
#         db: AsyncSession,
#         user: User,
#         active: bool,
#     ) -> User:

#         user.is_active = active

#         profile = user.delivery_profile

#         if profile is not None and not active:
#             profile.is_online = False
#             profile.is_available = False

#         await db.commit()
#         await db.refresh(user)

#         return user
    
    
#     def delivery_partner_response(user: User) -> dict:

#         profile = user.delivery_profile

#         return {
#             "id": user.id,

#             "full_name": user.full_name,
#             "email": user.email,
#             "phone": user.phone,

#             "role": user.role,

#             "is_active": user.is_active,
#             "is_verified": user.is_verified,

#             "vehicle_type": (
#                 profile.vehicle_type
#                 if profile
#                 else None
#             ),

#             "vehicle_number": (
#                 profile.vehicle_number
#                 if profile
#                 else None
#             ),

#             "is_online": (
#                 profile.is_online
#                 if profile
#                 else False
#             ),

#             "is_available": (
#                 profile.is_available
#                 if profile
#                 else False
#             ),

#             "is_approved": (
#                 profile.is_approved
#                 if profile
#                 else False
#             ),

#             "current_latitude": (
#                 float(profile.current_latitude)
#                 if profile and profile.current_latitude is not None
#                 else None
#             ),

#             "current_longitude": (
#                 float(profile.current_longitude)
#                 if profile and profile.current_longitude is not None
#                 else None
#             ),

#             "last_location_at": (
#                 profile.last_location_at
#                 if profile
#                 else None
#             ),

#             "created_at": user.created_at,
#         }





# from sqlalchemy import or_, select
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.delivery_partner import DeliveryPartnerProfile

from app.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerUpdate,
)


from app.utils.phone import (
    normalize_indian_phone,
)


from app.core.security import hash_password


# IMPORTANT:
# Replace this import with your actual existing password hash function.
from app.core.security import hash_password


def delivery_partner_response(user: User) -> dict:
    profile = user.delivery_profile

    return {
        "id": user.id,

        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,

        "role": user.role,

        "is_active": user.is_active,
        "is_verified": user.is_verified,

        "vehicle_type": (
            profile.vehicle_type
            if profile
            else None
        ),

        "vehicle_number": (
            profile.vehicle_number
            if profile
            else None
        ),

        "is_online": (
            profile.is_online
            if profile
            else False
        ),

        "is_available": (
            profile.is_available
            if profile
            else False
        ),

        "is_approved": (
            profile.is_approved
            if profile
            else False
        ),

        "current_latitude": (
            float(profile.current_latitude)
            if profile and profile.current_latitude is not None
            else None
        ),

        "current_longitude": (
            float(profile.current_longitude)
            if profile and profile.current_longitude is not None
            else None
        ),

        "last_location_at": (
            profile.last_location_at
            if profile
            else None
        ),

        "created_at": user.created_at,
    }


class DeliveryPartnerService:

    # @staticmethod
    # async def create(
    #     db: AsyncSession,
    #     data: DeliveryPartnerCreate,
    # ) -> User:

    #     conditions = [
    #         User.phone == data.phone.strip(),
    #     ]

    #     if data.email:
    #         conditions.append(
    #             User.email == str(data.email).lower()
    #         )

    #     result = await db.execute(
    #         select(User).where(
    #             or_(*conditions)
    #         )
    #     )

    #     existing_user = result.scalar_one_or_none()

    #     if existing_user:
    #         if existing_user.phone == data.phone.strip():
    #             raise ValueError(
    #                 "A user with this phone number already exists."
    #             )

    #         raise ValueError(
    #             "A user with this email already exists."
    #         )

    #     user = User(
    #         full_name=data.full_name.strip(),

    #         email=(
    #             str(data.email).lower()
    #             if data.email
    #             else None
    #         ),

    #         phone=data.phone.strip(),

    #         password_hash=hash_password(
    #             data.password
    #         ),

    #         role="DELIVERY_PARTNER",

    #         is_active=True,
    #         is_verified=True,
    #     )

    #     db.add(user)

    #     await db.flush()

    #     profile = DeliveryPartnerProfile(
    #         user_id=user.id,

    #         vehicle_type=(
    #             data.vehicle_type.strip()
    #             if data.vehicle_type
    #             else None
    #         ),

    #         vehicle_number=(
    #             data.vehicle_number.strip().upper()
    #             if data.vehicle_number
    #             else None
    #         ),

    #         is_online=False,

    #         is_available=True,

    #         is_approved=False,
    #     )

    #     db.add(profile)

    #     await db.commit()

    #     return await DeliveryPartnerService.get_by_id(
    #         db,
    #         user.id,
    #     )



    @staticmethod
    async def create(
        db: AsyncSession,
        data: DeliveryPartnerCreate,
    ) -> User:

        # =========================================================
        # NORMALIZE INPUT
        # =========================================================

        # phone = data.phone.strip()
        phone = normalize_indian_phone(
    data.phone
)

        email = (
            str(data.email)
            .lower()
            .strip()
            if data.email
            else None
        )

        # =========================================================
        # CHECK PHONE SEPARATELY
        # =========================================================

        result = await db.execute(
            select(User).where(
                User.phone == phone
            )
        )

        existing_phone = (
            result.scalar_one_or_none()
        )

        if existing_phone:
            raise ValueError(
                "A user with this phone number already exists."
            )

        # =========================================================
        # CHECK EMAIL SEPARATELY
        # =========================================================

        if email:

            result = await db.execute(
                select(User).where(
                    User.email == email
                )
            )

            existing_email = (
                result.scalar_one_or_none()
            )

            if existing_email:
                raise ValueError(
                    "A user with this email already exists."
                )

        # =========================================================
        # CREATE USER
        # =========================================================

        user = User(
            full_name=(
                data.full_name.strip()
            ),

            email=email,

            phone=phone,

            password_hash=hash_password(
                data.password
            ),

            role="DELIVERY_PARTNER",

            is_active=True,

            is_verified=True,
        )

        db.add(user)

        await db.flush()

        # =========================================================
        # CREATE DELIVERY PROFILE
        # =========================================================

        profile = DeliveryPartnerProfile(
            user_id=user.id,

            vehicle_type=(
                data.vehicle_type.strip()
                if data.vehicle_type
                else None
            ),

            vehicle_number=(
                data.vehicle_number
                .strip()
                .upper()
                if data.vehicle_number
                else None
            ),

            is_online=False,

            is_available=True,

            is_approved=False,
        )

        db.add(profile)

        await db.commit()

        return (
            await DeliveryPartnerService
            .get_by_id(
                db,
                user.id,
            )
        )
        
    
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        user_id: int,
    ) -> User | None:

        result = await db.execute(
            select(User)
            .options(
                selectinload(
                    User.delivery_profile
                )
            )
            .where(
                User.id == user_id,
                User.role == "DELIVERY_PARTNER",
            )
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def list_all(
        db: AsyncSession,
    ) -> list[User]:

        result = await db.execute(
            select(User)
            .options(
                selectinload(
                    User.delivery_profile
                )
            )
            .where(
                User.role == "DELIVERY_PARTNER"
            )
            .order_by(
                User.created_at.desc()
            )
        )

        return list(
            result.scalars().all()
        )


    @staticmethod
    async def update(
        db: AsyncSession,
        user: User,
        data: DeliveryPartnerUpdate,
    ) -> User:

        if data.full_name is not None:
            user.full_name = (
                data.full_name.strip()
            )

        if data.email is not None:
            email = str(
                data.email
            ).lower()

            result = await db.execute(
                select(User).where(
                    User.email == email,
                    User.id != user.id,
                )
            )

            if result.scalar_one_or_none():
                raise ValueError(
                    "Another user already uses this email."
                )

            user.email = email

        if data.phone is not None:
            phone = data.phone.strip()

            result = await db.execute(
                select(User).where(
                    User.phone == phone,
                    User.id != user.id,
                )
            )

            if result.scalar_one_or_none():
                raise ValueError(
                    "Another user already uses this phone number."
                )

            user.phone = phone

        profile = user.delivery_profile

        if profile is None:
            raise ValueError(
                "Delivery partner profile does not exist."
            )

        if data.vehicle_type is not None:
            profile.vehicle_type = (
                data.vehicle_type.strip()
                or None
            )

        if data.vehicle_number is not None:
            profile.vehicle_number = (
                data.vehicle_number
                .strip()
                .upper()
                or None
            )

        await db.commit()

        return await DeliveryPartnerService.get_by_id(
            db,
            user.id,
        )


    # @staticmethod
    # async def set_approval(
    #     db: AsyncSession,
    #     user: User,
    #     approved: bool,
    # ) -> User:

    #     profile = user.delivery_profile

    #     if profile is None:
    #         raise ValueError(
    #             "Delivery partner profile does not exist."
    #         )

    #     profile.is_approved = approved

    #     if approved:
    #         # profile.is_available = True
    #         await db.flush()

    #         await DeliveryAssignmentService.sync_partner_availability(
    #             db,
    #             partner,
    #         )

    #     else:
    #         profile.is_online = False
    #         profile.is_available = False

    #     await db.commit()

    #     return await DeliveryPartnerService.get_by_id(
    #         db,
    #         user.id,
    #     )



    @staticmethod
    async def set_approval(
        db: AsyncSession,
        user: User,
        approved: bool,
    ) -> User:

        profile = user.delivery_profile

        if profile is None:
            raise ValueError(
                "Delivery partner profile does not exist."
            )

        profile.is_approved = approved

        if not approved:
            profile.is_online = False
            profile.is_available = False

        else:
            # Approval itself should not blindly make
            # a busy partner available.
            from app.services.delivery_assignment_service import (
                DeliveryAssignmentService,
            )

            active_count = (
                await DeliveryAssignmentService
                .get_active_delivery_count(
                    db,
                    user.id,
                )
            )

            profile.is_available = bool(
                profile.is_online
                and active_count == 0
            )

        await db.commit()

        return await DeliveryPartnerService.get_by_id(
            db,
            user.id,
        )
        
        


    # =========================================================
    # CHANGE PASSWORD
    # =========================================================

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        new_password: str,
    ) -> User:

        new_password = (
            new_password.strip()
        )

        if len(new_password) < 8:
            raise ValueError(
                "Password must be at least 8 characters."
            )

        user.password_hash = (
            hash_password(
                new_password
            )
        )

        await db.commit()

        await db.refresh(
            user
        )

        return user


    @staticmethod
    async def set_active(
        db: AsyncSession,
        user: User,
        active: bool,
    ) -> User:

        user.is_active = active

        profile = user.delivery_profile

        if profile and not active:
            profile.is_online = False
            profile.is_available = False

        await db.commit()

        return await DeliveryPartnerService.get_by_id(
            db,
            user.id,
        )