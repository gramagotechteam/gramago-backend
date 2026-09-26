# # from pathlib import Path

# # import firebase_admin

# # from firebase_admin import credentials

# # from app.core.config import settings


# # def initialize_firebase() -> None:

# #     # Already initialized.
# #     if firebase_admin._apps:
# #         return


# #     credentials_path = (
# #         settings.FIREBASE_CREDENTIALS_PATH
# #     )


# #     if not credentials_path:

# #         print(
# #             "WARNING: Firebase credentials "
# #             "path is not configured."
# #         )

# #         return


# #     path = Path(
# #         credentials_path
# #     )


# #     if not path.is_absolute():

# #         path = Path.cwd() / path


# #     if not path.exists():

# #         print(
# #             "WARNING: Firebase credentials "
# #             f"file not found: {path}"
# #         )

# #         return


# #     cred = credentials.Certificate(
# #         str(path)
# #     )


# #     firebase_admin.initialize_app(
# #         cred
# #     )


# #     print(
# #         "Firebase Admin initialized successfully."
# #     )


# # def firebase_is_ready() -> bool:

# #     return bool(
# #         firebase_admin._apps
# #     )







# from pathlib import Path

# import firebase_admin

# from firebase_admin import (
#     credentials,
# )

# from app.core.config import settings


# def firebase_is_ready() -> bool:

#     try:

#         firebase_admin.get_app()

#         return True

#     except ValueError:

#         return False


# def initialize_firebase() -> None:

#     print(
#         "========================================"
#     )

#     print(
#         "Initializing Firebase Admin..."
#     )


#     # =========================================================
#     # ALREADY INITIALIZED
#     # =========================================================

#     if firebase_is_ready():

#         print(
#             "Firebase Admin already initialized."
#         )

#         print(
#             "========================================"
#         )

#         return


#     # =========================================================
#     # READ CONFIG
#     # =========================================================

#     credentials_path = (
#         settings.FIREBASE_CREDENTIALS_PATH
#     )


#     print(
#         "Firebase credentials config:",
#         credentials_path,
#     )


#     if not credentials_path:

#         print(
#             "ERROR: FIREBASE_CREDENTIALS_PATH "
#             "is not configured."
#         )

#         print(
#             "========================================"
#         )

#         return


#     # =========================================================
#     # RESOLVE FILE PATH
#     # =========================================================

#     path = Path(
#         credentials_path
#     )


#     if not path.is_absolute():

#         path = (
#             Path.cwd()
#             / path
#         )


#     path = path.resolve()


#     print(
#         "Resolved Firebase credentials path:",
#         path,
#     )


#     print(
#         "Credentials file exists:",
#         path.exists(),
#     )


#     if not path.exists():

#         print(
#             "ERROR: Firebase service account "
#             "file does not exist."
#         )

#         print(
#             "========================================"
#         )

#         return


#     # =========================================================
#     # INITIALIZE FIREBASE ADMIN
#     # =========================================================

#     try:

#         cred = (
#             credentials.Certificate(
#                 str(path)
#             )
#         )


#         firebase_admin.initialize_app(
#             cred
#         )


#         print(
#             "Firebase Admin initialized "
#             "successfully."
#         )


#         print(
#             "Firebase ready:",
#             firebase_is_ready(),
#         )


#     except Exception as exc:

#         print(
#             "FIREBASE INITIALIZATION ERROR:"
#         )

#         print(
#             type(exc).__name__,
#         )

#         print(
#             str(exc),
#         )


#     print(
#         "========================================"
#     )





import json
from pathlib import Path

import firebase_admin
from firebase_admin import credentials

from app.core.config import settings


def firebase_is_ready() -> bool:
    try:
        firebase_admin.get_app()
        return True
    except ValueError:
        return False


def initialize_firebase() -> None:
    print("========================================")
    print("Initializing Firebase Admin...")

    # =========================================================
    # ALREADY INITIALIZED
    # =========================================================

    if firebase_is_ready():
        print("Firebase Admin already initialized.")
        print("========================================")
        return

    # =========================================================
    # OPTION 1:
    # FIREBASE JSON FROM ENVIRONMENT VARIABLE
    #
    # Recommended for Railway / production.
    # =========================================================

    credentials_json = settings.FIREBASE_CREDENTIALS_JSON

    if credentials_json:
        try:
            service_account_info = json.loads(credentials_json)

            cred = credentials.Certificate(
                service_account_info
            )

            firebase_admin.initialize_app(
                cred
            )

            print(
                "Firebase Admin initialized "
                "successfully from environment."
            )

            print(
                "Firebase ready:",
                firebase_is_ready(),
            )

            print("========================================")

            return

        except Exception as exc:
            print(
                "FIREBASE ENV INITIALIZATION ERROR:"
            )

            print(
                type(exc).__name__,
            )

            print(
                str(exc),
            )

            print("========================================")

            return

    # =========================================================
    # OPTION 2:
    # FIREBASE JSON FILE PATH
    #
    # Useful for local development.
    # =========================================================

    credentials_path = settings.FIREBASE_CREDENTIALS_PATH

    if not credentials_path:
        print(
            "ERROR: Neither FIREBASE_CREDENTIALS_JSON "
            "nor FIREBASE_CREDENTIALS_PATH "
            "is configured."
        )

        print("========================================")

        return

    path = Path(credentials_path)

    if not path.is_absolute():
        path = Path.cwd() / path

    path = path.resolve()

    print(
        "Firebase credentials path configured."
    )

    print(
        "Credentials file exists:",
        path.exists(),
    )

    if not path.exists():
        print(
            "ERROR: Firebase service account "
            "file does not exist."
        )

        print("========================================")

        return

    # =========================================================
    # INITIALIZE FIREBASE FROM FILE
    # =========================================================

    try:
        cred = credentials.Certificate(
            str(path)
        )

        firebase_admin.initialize_app(
            cred
        )

        print(
            "Firebase Admin initialized "
            "successfully from file."
        )

        print(
            "Firebase ready:",
            firebase_is_ready(),
        )

    except Exception as exc:
        print(
            "FIREBASE FILE INITIALIZATION ERROR:"
        )

        print(
            type(exc).__name__,
        )

        print(
            str(exc),
        )

    print("========================================")