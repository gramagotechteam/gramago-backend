# # # # import asyncio
# # # # import selectors

# # # # # Force Psycopg to use SelectorEventLoop on Windows
# # # # asyncio.set_event_loop_policy(
# # # #     asyncio.WindowsSelectorEventLoopPolicy()
# # # # )



# # # # import asyncio

# # # # from sqlalchemy import select

# # # # from app.core.security import hash_password
# # # # from app.db.session import AsyncSessionLocal
# # # # from app.models.user import User


# # # # async def create_super_admin():

# # # #     async with AsyncSessionLocal() as db:

# # # #         email = "ask@gmail.com"
# # # #         phone = "9390370111"

# # # #         result = await db.execute(
# # # #             select(User).where(
# # # #                 User.email == email
# # # #             )
# # # #         )

# # # #         existing = result.scalar_one_or_none()

# # # #         if existing:
# # # #             print(
# # # #                 "Super admin already exists"
# # # #             )
# # # #             return

# # # #         admin = User(
# # # #             full_name="GramaGo Admin",
# # # #             email=email,
# # # #             phone=phone,
# # # #             password_hash=hash_password(
# # # #                 "Ask@123"
# # # #             ),
# # # #             role="SUPER_ADMIN",
# # # #             is_active=True,
# # # #             is_verified=True,
# # # #         )

# # # #         db.add(admin)

# # # #         await db.commit()

# # # #         print(
# # # #             "Super admin created successfully"
# # # #         )


# # # # if __name__ == "__main__":
# # # #     asyncio.run(
# # # #         create_super_admin()
# # # #     )




# # # import asyncio
# # # import sys
# # # import os
# # # from pathlib import Path

# # # # --- Fix import path ---
# # # BASE_DIR = Path(__file__).resolve().parents[2]  # go up to gramago-backend
# # # sys.path.append(str(BASE_DIR))

# # # # --- Force Psycopg to use SelectorEventLoop on Windows ---
# # # if sys.platform.startswith("win"):
# # #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# # # from sqlalchemy import select
# # # from app.core.security import hash_password
# # # from app.db.session import AsyncSessionLocal
# # # from app.models.user import User


# # # async def create_super_admin():
# # #     async with AsyncSessionLocal() as db:
# # #         email = "ask@gmail.com"
# # #         phone = "9390370111"

# # #         result = await db.execute(select(User).where(User.email == email))
# # #         existing = result.scalar_one_or_none()

# # #         if existing:
# # #             print("Super admin already exists")
# # #             return

# # #         admin = User(
# # #             full_name="GramaGo Admin",
# # #             email=email,
# # #             phone=phone,
# # #             password_hash=hash_password("Ask@123"),
# # #             role="SUPER_ADMIN",
# # #             is_active=True,
# # #             is_verified=True,
# # #         )

# # #         db.add(admin)
# # #         await db.commit()
# # #         print("Super admin created successfully")


# # # if __name__ == "__main__":
# # #     asyncio.run(create_super_admin())





# # import asyncio
# # import sys
# # from pathlib import Path

# # from sqlalchemy import select


# # # --------------------------------------------------
# # # Add project root to Python path
# # # --------------------------------------------------

# # BASE_DIR = Path(__file__).resolve().parents[1]

# # if str(BASE_DIR) not in sys.path:
# #     sys.path.insert(0, str(BASE_DIR))


# # # --------------------------------------------------
# # # IMPORTANT:
# # # Import all SQLAlchemy models before using User.
# # # This resolves relationships such as "RefreshToken".
# # # --------------------------------------------------

# # from app.db import models  # noqa: F401

# # from app.core.security import hash_password
# # from app.db.session import AsyncSessionLocal
# # from app.models.user import User


# # # --------------------------------------------------
# # # Super Admin Configuration
# # # --------------------------------------------------

# # SUPER_ADMIN_NAME = "GramaGo Super Admin"
# # SUPER_ADMIN_EMAIL = "ask@gmail.com"
# # SUPER_ADMIN_PHONE = "9390370111"

# # # Local development only.
# # # Change this immediately after first login.
# # SUPER_ADMIN_PASSWORD = "ChangeThisPassword123!"


# # # --------------------------------------------------
# # # Create Super Admin
# # # --------------------------------------------------

# # async def create_super_admin():

# #     async with AsyncSessionLocal() as db:

# #         # Check email
# #         result = await db.execute(
# #             select(User).where(
# #                 User.email == SUPER_ADMIN_EMAIL
# #             )
# #         )

# #         existing_email = result.scalar_one_or_none()

# #         if existing_email:
# #             print(
# #                 f"User already exists with email: "
# #                 f"{SUPER_ADMIN_EMAIL}"
# #             )

# #             print(
# #                 f"Role: {existing_email.role}"
# #             )

# #             return

# #         # Check phone
# #         result = await db.execute(
# #             select(User).where(
# #                 User.phone == SUPER_ADMIN_PHONE
# #             )
# #         )

# #         existing_phone = result.scalar_one_or_none()

# #         if existing_phone:
# #             print(
# #                 f"User already exists with phone: "
# #                 f"{SUPER_ADMIN_PHONE}"
# #             )

# #             print(
# #                 f"Role: {existing_phone.role}"
# #             )

# #             return

# #         # Create super admin
# #         super_admin = User(
# #             full_name=SUPER_ADMIN_NAME,
# #             email=SUPER_ADMIN_EMAIL,
# #             phone=SUPER_ADMIN_PHONE,
# #             password_hash=hash_password(
# #                 SUPER_ADMIN_PASSWORD
# #             ),
# #             role="SUPER_ADMIN",
# #             is_active=True,
# #             is_verified=True,
# #         )

# #         try:

# #             db.add(super_admin)

# #             await db.commit()

# #             await db.refresh(super_admin)

# #             print()
# #             print(
# #                 "GramaGo Super Admin created successfully!"
# #             )
# #             print("-----------------------------------")
# #             print(
# #                 f"ID: {super_admin.id}"
# #             )
# #             print(
# #                 f"Name: {super_admin.full_name}"
# #             )
# #             print(
# #                 f"Email: {super_admin.email}"
# #             )
# #             print(
# #                 f"Phone: {super_admin.phone}"
# #             )
# #             print(
# #                 f"Role: {super_admin.role}"
# #             )
# #             print("-----------------------------------")
# #             print()
# #             print(
# #                 "IMPORTANT: Change the default password "
# #                 "after first login."
# #             )

# #         except Exception as exc:

# #             await db.rollback()

# #             print()
# #             print(
# #                 "Failed to create Super Admin."
# #             )

# #             print(
# #                 f"Error: {exc}"
# #             )

# #             raise


# # # --------------------------------------------------
# # # Entry Point
# # # --------------------------------------------------

# # if __name__ == "__main__":

# #     asyncio.run(
# #         create_super_admin()
# #     )




# import asyncio
# import sys
# from pathlib import Path

# from sqlalchemy import select

# # --------------------------------------------------
# # Fix event loop policy for Psycopg on Windows
# # --------------------------------------------------
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# # --------------------------------------------------
# # Add project root to Python path
# # --------------------------------------------------
# BASE_DIR = Path(__file__).resolve().parents[1]
# if str(BASE_DIR) not in sys.path:
#     sys.path.insert(0, str(BASE_DIR))

# # --------------------------------------------------
# # Import all SQLAlchemy models before using User
# # --------------------------------------------------
# from app.db import models  # noqa: F401
# from app.core.security import hash_password
# from app.db.session import AsyncSessionLocal
# from app.models.user import User

# # --------------------------------------------------
# # Super Admin Configuration
# # --------------------------------------------------
# SUPER_ADMIN_NAME = "GramaGo Super Admin"
# SUPER_ADMIN_EMAIL = "ask@gmail.com"
# SUPER_ADMIN_PHONE = "9390370111"
# SUPER_ADMIN_PASSWORD = "Ask@1234"  # change after first login

# # --------------------------------------------------
# # Create Super Admin
# # --------------------------------------------------
# async def create_super_admin():
#     async with AsyncSessionLocal() as db:
#         # Check email
#         result = await db.execute(select(User).where(User.email == SUPER_ADMIN_EMAIL))
#         existing_email = result.scalar_one_or_none()
#         if existing_email:
#             print(f"User already exists with email: {SUPER_ADMIN_EMAIL}")
#             print(f"Role: {existing_email.role}")
#             return

#         # Check phone
#         result = await db.execute(select(User).where(User.phone == SUPER_ADMIN_PHONE))
#         existing_phone = result.scalar_one_or_none()
#         if existing_phone:
#             print(f"User already exists with phone: {SUPER_ADMIN_PHONE}")
#             print(f"Role: {existing_phone.role}")
#             return

#         # Create super admin
#         super_admin = User(
#             full_name=SUPER_ADMIN_NAME,
#             email=SUPER_ADMIN_EMAIL,
#             phone=SUPER_ADMIN_PHONE,
#             password_hash=hash_password(SUPER_ADMIN_PASSWORD),
#             role="SUPER_ADMIN",
#             is_active=True,
#             is_verified=True,
#         )

#         try:
#             db.add(super_admin)
#             await db.commit()
#             await db.refresh(super_admin)

#             print("\nGramaGo Super Admin created successfully!")
#             print("-----------------------------------")
#             print(f"ID: {super_admin.id}")
#             print(f"Name: {super_admin.full_name}")
#             print(f"Email: {super_admin.email}")
#             print(f"Phone: {super_admin.phone}")
#             print(f"Role: {super_admin.role}")
#             print("-----------------------------------")
#             print("\nIMPORTANT: Change the default password after first login.")

#         except Exception as exc:
#             await db.rollback()
#             print("\nFailed to create Super Admin.")
#             print(f"Error: {exc}")
#             raise

# # --------------------------------------------------
# # Entry Point
# # --------------------------------------------------
# if __name__ == "__main__":
#     asyncio.run(create_super_admin())



import asyncio
import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def main():
    print("Create GramaGo Admin")
    print("====================")

    full_name = input("Full name: ").strip()
    email = input("Email: ").strip().lower()
    phone = input("Phone: ").strip()
    password = getpass.getpass("Password: ")

    if len(password) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )

    async with AsyncSessionLocal() as db:

        existing = await db.execute(
            select(User).where(
                (User.email == email)
                | (User.phone == phone)
            )
        )

        if existing.scalar_one_or_none():
            print("User already exists.")
            return

        admin = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            role="SUPER_ADMIN",
            is_active=True,
            is_verified=True,
        )

        db.add(admin)

        await db.commit()
        await db.refresh(admin)

        print("Admin created successfully.")
        print(f"ID: {admin.id}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")


if __name__ == "__main__":
    asyncio.run(main())