# # # # app/core/delivery_firebase.py

# # # import os

# # # import firebase_admin

# # # from firebase_admin import credentials


# # # DELIVERY_FIREBASE_APP_NAME = "gramago_delivery"


# # # def initialize_delivery_firebase():
# # #     try:
# # #         return firebase_admin.get_app(
# # #             DELIVERY_FIREBASE_APP_NAME
# # #         )
# # #     except ValueError:
# # #         pass

# # #     credential_path = os.getenv(
# # #         "FIREBASE_CREDENTIALS_DELIVERY_PATH"
# # #     )

# # #     if not credential_path:
# # #         raise RuntimeError(
# # #             "FIREBASE_CREDENTIALS_DELIVERY_PATH "
# # #             "is not configured"
# # #         )

# # #     cred = credentials.Certificate(
# # #         credential_path
# # #     )

# # #     app = firebase_admin.initialize_app(
# # #         cred,
# # #         name=DELIVERY_FIREBASE_APP_NAME,
# # #     )

# # #     return app



# # import os

# # import firebase_admin

# # from firebase_admin import credentials
# # from firebase_admin import App


# # DELIVERY_FIREBASE_APP_NAME = "gramago_delivery"


# # def get_delivery_firebase_app() -> App:
# #     """
# #     Return the dedicated Firebase Admin app used only
# #     for the GramaGo Delivery application.

# #     This does NOT use or modify the customer Firebase app.
# #     """

# #     try:
# #         return firebase_admin.get_app(
# #             DELIVERY_FIREBASE_APP_NAME
# #         )

# #     except ValueError:
# #         pass

# #     credential_path = os.getenv(
# #         "FIREBASE_CREDENTIALS_DELIVERY_PATH"
# #     )

# #     if not credential_path:
# #         raise RuntimeError(
# #             "FIREBASE_CREDENTIALS_DELIVERY_PATH "
# #             "is not configured."
# #         )

# #     if not os.path.exists(
# #         credential_path
# #     ):
# #         raise RuntimeError(
# #             "Delivery Firebase credentials file "
# #             f"not found: {credential_path}"
# #         )

# #     cred = credentials.Certificate(
# #         credential_path
# #     )

# #     delivery_app = (
# #         firebase_admin.initialize_app(
# #             cred,
# #             name=DELIVERY_FIREBASE_APP_NAME,
# #         )
# #     )

# #     return delivery_app




# import os
# from pathlib import Path

# import firebase_admin

# from dotenv import load_dotenv
# from firebase_admin import App, credentials


# # ============================================================
# # PROJECT PATHS
# # ============================================================

# # app/core/delivery_firebase.py
# #
# # parents[0] -> core
# # parents[1] -> app
# # parents[2] -> gramago-backend
# BASE_DIR = Path(__file__).resolve().parents[2]


# # ============================================================
# # LOAD .ENV
# # ============================================================

# ENV_FILE = BASE_DIR / ".env"

# load_dotenv(
#     dotenv_path=ENV_FILE,
# )


# # ============================================================
# # DELIVERY FIREBASE APP
# # ============================================================

# DELIVERY_FIREBASE_APP_NAME = (
#     "gramago_delivery"
# )


# def get_delivery_firebase_app() -> App:
#     """
#     Get or initialize the Firebase Admin app dedicated
#     only to the GramaGo Delivery application.

#     This does not interfere with the existing
#     GramaGo Customer Firebase project.
#     """

#     # --------------------------------------------------------
#     # RETURN EXISTING INSTANCE
#     # --------------------------------------------------------

#     try:
#         return firebase_admin.get_app(
#             DELIVERY_FIREBASE_APP_NAME
#         )

#     except ValueError:
#         pass

#     # --------------------------------------------------------
#     # READ DELIVERY FIREBASE CREDENTIAL PATH
#     # --------------------------------------------------------

#     credential_path_value = os.getenv(
#         "FIREBASE_CREDENTIALS_DELIVERY_PATH"
#     )

#     if not credential_path_value:
#         raise RuntimeError(
#             "FIREBASE_CREDENTIALS_DELIVERY_PATH "
#             "is not configured."
#         )

#     # --------------------------------------------------------
#     # BUILD ABSOLUTE PATH
#     # --------------------------------------------------------

#     credential_path = Path(
#         credential_path_value
#     )

#     # If .env contains:
#     #
#     # secrets/file.json
#     #
#     # resolve it relative to gramago-backend/
#     if not credential_path.is_absolute():
#         credential_path = (
#             BASE_DIR
#             / credential_path
#         )

#     credential_path = (
#         credential_path.resolve()
#     )

#     # --------------------------------------------------------
#     # VERIFY FILE
#     # --------------------------------------------------------

#     if not credential_path.exists():
#         raise RuntimeError(
#             "Delivery Firebase credentials "
#             "file was not found at: "
#             f"{credential_path}"
#         )

#     # --------------------------------------------------------
#     # CREATE FIREBASE CREDENTIAL
#     # --------------------------------------------------------

#     cred = credentials.Certificate(
#         str(
#             credential_path
#         )
#     )

#     # --------------------------------------------------------
#     # INITIALIZE NAMED DELIVERY FIREBASE APP
#     # --------------------------------------------------------

#     delivery_app = (
#         firebase_admin.initialize_app(
#             cred,
#             name=(
#                 DELIVERY_FIREBASE_APP_NAME
#             ),
#         )
#     )

#     print(
#         "DELIVERY FIREBASE INITIALIZED:",
#         DELIVERY_FIREBASE_APP_NAME,
#     )

#     print(
#         "DELIVERY FIREBASE CREDENTIALS:",
#         credential_path,
#     )

#     return delivery_app

import os
from pathlib import Path

import firebase_admin

from dotenv import load_dotenv
from firebase_admin import App, credentials


# ============================================================
# PROJECT BASE DIRECTORY
# ============================================================

# Current file:
# gramago-backend/app/core/delivery_firebase.py
#
# parents[0] = core
# parents[1] = app
# parents[2] = gramago-backend
BASE_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# LOAD .ENV FILE
# ============================================================

ENV_FILE = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
)


# ============================================================
# DELIVERY FIREBASE CONFIG
# ============================================================

DELIVERY_FIREBASE_APP_NAME = "gramago_delivery"


def get_delivery_firebase_app() -> App:
    """
    Return the Firebase Admin app used only
    for the GramaGo Delivery application.
    """

    # ========================================================
    # RETURN EXISTING DELIVERY FIREBASE APP
    # ========================================================

    try:
        return firebase_admin.get_app(
            DELIVERY_FIREBASE_APP_NAME
        )

    except ValueError:
        pass

    # ========================================================
    # READ DELIVERY CREDENTIAL PATH
    # ========================================================

    credential_path_value = os.getenv(
        "FIREBASE_CREDENTIALS_DELIVERY_PATH"
    )

    if not credential_path_value:
        raise RuntimeError(
            "FIREBASE_CREDENTIALS_DELIVERY_PATH "
            "is not configured."
        )

    # ========================================================
    # CONVERT TO PATH
    # ========================================================

    credential_path = Path(
        credential_path_value
    )

    # If .env contains a relative path such as:
    #
    # secrets/file.json
    #
    # resolve it relative to gramago-backend/
    if not credential_path.is_absolute():
        credential_path = (
            BASE_DIR
            / credential_path
        )

    credential_path = (
        credential_path.resolve()
    )

    # ========================================================
    # VERIFY CREDENTIAL FILE EXISTS
    # ========================================================

    if not credential_path.exists():
        raise RuntimeError(
            "Delivery Firebase credentials file "
            "was not found at: "
            f"{credential_path}"
        )

    # ========================================================
    # CREATE FIREBASE CREDENTIAL
    # ========================================================

    cred = credentials.Certificate(
        str(
            credential_path
        )
    )

    # ========================================================
    # INITIALIZE NAMED DELIVERY FIREBASE APP
    # ========================================================

    delivery_app = (
        firebase_admin.initialize_app(
            cred,
            name=(
                DELIVERY_FIREBASE_APP_NAME
            ),
        )
    )

    print(
        "DELIVERY FIREBASE INITIALIZED:",
        DELIVERY_FIREBASE_APP_NAME,
    )

    print(
        "DELIVERY FIREBASE CREDENTIALS:",
        credential_path,
    )

    return delivery_app
