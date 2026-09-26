# import secrets
# from hmac import compare_digest

# from fastapi import (
#     Form,
#     HTTPException,
#     Request,
#     status,
# )


# CSRF_SESSION_KEY = "_admin_csrf_token"


# def get_csrf_token(
#     request: Request,
# ) -> str:

#     token = request.session.get(
#         CSRF_SESSION_KEY
#     )

#     if not token:

#         token = secrets.token_urlsafe(32)

#         request.session[
#             CSRF_SESSION_KEY
#         ] = token

#     return token


# async def validate_csrf(
#     request: Request,

#     csrf_token: str = Form(
#         ...,
#         alias="_csrf_token",
#     ),
# ):

#     session_token = request.session.get(
#         CSRF_SESSION_KEY
#     )

#     if (
#         not session_token
#         or not csrf_token
#         or not compare_digest(
#             session_token,
#             csrf_token,
#         )
#     ):

#         raise HTTPException(
#             status_code=(
#                 status.HTTP_403_FORBIDDEN
#             ),
#             detail="Invalid CSRF token",
#         )



import secrets
from hmac import compare_digest

from fastapi import (
    Form,
    HTTPException,
    Request,
    status,
)


CSRF_SESSION_KEY = "_admin_csrf_token"


def get_csrf_token(
    request: Request,
) -> str:

    token = request.session.get(
        CSRF_SESSION_KEY
    )

    if not token:

        token = secrets.token_urlsafe(32)

        request.session[
            CSRF_SESSION_KEY
        ] = token

    return token


async def validate_csrf(
    request: Request,

    csrf_token: str = Form(
        ...,
        alias="_csrf_token",
    ),
):

    session_token = request.session.get(
        CSRF_SESSION_KEY
    )

    if (
        not session_token
        or not csrf_token
        or not compare_digest(
            session_token,
            csrf_token,
        )
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="Invalid CSRF token",
        )