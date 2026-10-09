
# from fastapi import HTTPException, Request
# from fastapi.exception_handlers import (
#     http_exception_handler,
# )
# from fastapi.responses import JSONResponse

# from app.web.templates import templates



# from fastapi import FastAPI

# from app.api.v1.router import api_router
# from app.core.config import settings


# from app.core.firebase import (
#     initialize_firebase,
# )


# from contextlib import (
#     asynccontextmanager,
# )

# from fastapi import FastAPI

# from app.core.firebase import (
#     initialize_firebase,
# )


# @asynccontextmanager
# async def lifespan(
#     app: FastAPI,
# ):

#     initialize_firebase()

#     yield


# app = FastAPI(

#     title=settings.APP_NAME,

#     version="1.0.0",

#     lifespan=lifespan,
# )

# app = FastAPI(
#     title=settings.APP_NAME,
#     version="1.0.0",
# )


# app.include_router(
#     api_router,
#     prefix=settings.API_V1_PREFIX,
# )


# # app.include_router(
# #     api_router,
# #     prefix=settings.API_V1_PREFIX,
# # )

# from starlette.middleware.sessions import (
#     SessionMiddleware,
# )

# from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import settings

# app.add_middleware(
#     SessionMiddleware,
#     secret_key=settings.JWT_SECRET_KEY,
#     session_cookie="gramago_admin_session",
#     max_age=60 * 60 * 8,
#     same_site="lax",
#     https_only=(
#         settings.APP_ENV == "production"
#     ),
# )


# app.add_middleware(
#     CORSMiddleware,

#     allow_origin_regex=(
#         r"http://(localhost|127\.0\.0\.1)(:\d+)?"
#     ),

#     allow_credentials=True,

#     allow_methods=["*"],

#     allow_headers=["*"],
# )

# from fastapi.staticfiles import StaticFiles

# app.mount(
#     "/static",
#     StaticFiles(
#         directory="app/static"
#     ),
#     name="static",
# )

# from app.web.router import (
#     admin_web_router,
# )


# app.include_router(
#     admin_web_router
# )



# from fastapi import Depends
# from sqlalchemy import text
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db


# @app.get("/health")
# async def health_check(
#     db: AsyncSession = Depends(get_db)
# ):
#     await db.execute(text("SELECT 1"))

#     return {
#         "success": True,
#         "status": "healthy",
#         "database": "connected"
#     }






# @app.exception_handler(HTTPException)
# async def custom_http_exception_handler(
#     request: Request,
#     exc: HTTPException,
# ):

#     if (
#         request.url.path.startswith(
#             "/admin"
#         )
#         and exc.status_code in {
#             403,
#             404,
#         }
#     ):

#         template = (
#             "admin/errors/403.html"
#             if exc.status_code == 403
#             else "admin/errors/404.html"
#         )

#         return templates.TemplateResponse(
#             request=request,
#             name=template,
#             context={
#                 "admin": None,
#                 "active_page": "",
#             },
#             status_code=exc.status_code,
#         )

#     return await http_exception_handler(
#         request,
#         exc,
#     )
    
    
    


# @app.exception_handler(Exception)
# async def admin_exception_handler(
#     request: Request,
#     exc: Exception,
# ):

#     if request.url.path.startswith(
#         "/admin"
#     ):

#         return templates.TemplateResponse(
#             request=request,
#             name="admin/errors/500.html",
#             context={
#                 "admin": None,
#                 "active_page": "",
#             },
#             status_code=500,
#         )

#     return JSONResponse(
#         status_code=500,
#         content={
#             "detail":
#                 "Internal server error"
#         },
#     )
















from contextlib import asynccontextmanager

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
)

from fastapi.exception_handlers import (
    http_exception_handler,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from fastapi.responses import (
    JSONResponse,
)

from fastapi.staticfiles import (
    StaticFiles,
)

from sqlalchemy import text

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from starlette.middleware.sessions import (
    SessionMiddleware,
)


from app.api.v1.router import (
    api_router,
)

from app.core.config import (
    settings,
)

from app.core.firebase import (
    firebase_is_ready,
    initialize_firebase,
)

from app.db.session import (
    get_db,
)

from app.web.router import (
    admin_web_router,
)

from app.web.templates import (
    templates,
)


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    print(
        "========================================"
    )

    print(
        "Starting GramaGo backend..."
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Initialize Firebase Admin SDK
    # --------------------------------------------------------

    initialize_firebase()


    print(
        "Firebase ready:",
        firebase_is_ready(),
    )


    yield


    print(
        "========================================"
    )

    print(
        "Stopping GramaGo backend..."
    )

    print(
        "========================================"
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(

    title=settings.APP_NAME,

    version="1.0.0",

    lifespan=lifespan,
    debug=settings.DEBUG,   # add this line
)


from fastapi import Request
from fastapi.responses import HTMLResponse

# Add this route after your routers are included
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        name="home.html",
         request=request,
    )

# ============================================================
# SESSION MIDDLEWARE
# ============================================================

app.add_middleware(

    SessionMiddleware,

    secret_key=(
        settings.JWT_SECRET_KEY
    ),

    session_cookie=(
        "gramago_admin_session"
    ),

    max_age=(
        60 * 60 * 8
    ),

    same_site="lax",

    https_only=(
        settings.APP_ENV
        == "production"
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    # CORSMiddleware,

    # allow_origin_regex=(
    #     r"http://"
    #     r"(localhost|127\.0\.0\.1)"
    #     r"(:\d+)?"
    # ),
    CORSMiddleware,
    allow_origins=["*"],   # ✅ allow all origins

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(

    "/static",

    StaticFiles(
        directory="app/static"
    ),

    name="static",
)


# ============================================================
# API ROUTER
# ============================================================

app.include_router(

    api_router,

    prefix=(
        settings.API_V1_PREFIX
    ),
)


# ============================================================
# ADMIN WEB ROUTER
# ============================================================

app.include_router(
    admin_web_router
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check(

    db:
        AsyncSession
        = Depends(get_db),

):

    await db.execute(
        text(
            "SELECT 1"
        )
    )


    return {

        "success": True,

        "status": "healthy",

        "database": "connected",

        "firebase":
            "connected"
            if firebase_is_ready()
            else "not_initialized",
    }


# ============================================================
# FIREBASE HEALTH CHECK
# ============================================================

@app.get("/firebase-health")
async def firebase_health():

    return {

        "success": True,

        "firebase_ready":
            firebase_is_ready(),
    }


# ============================================================
# HTTP EXCEPTION HANDLER
# ============================================================

@app.exception_handler(
    HTTPException
)
async def custom_http_exception_handler(

    request: Request,

    exc: HTTPException,

):

    # --------------------------------------------------------
    # Admin HTML error pages
    # --------------------------------------------------------

    if (

        request.url.path.startswith(
            "/admin"
        )

        and exc.status_code
        in {
            403,
            404,
        }

    ):

        template = (

            "admin/errors/403.html"

            if exc.status_code == 403

            else "admin/errors/404.html"
        )


        return templates.TemplateResponse(

            request=request,

            name=template,

            context={

                "admin": None,

                "active_page": "",
            },

            status_code=(
                exc.status_code
            ),
        )


    # --------------------------------------------------------
    # Normal API HTTP errors
    # --------------------------------------------------------

    return await http_exception_handler(

        request,

        exc,
    )


# ============================================================
# GENERAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(
    Exception
)
async def general_exception_handler(

    request: Request,

    exc: Exception,

):

    # --------------------------------------------------------
    # Admin HTML 500 page
    # --------------------------------------------------------

    if request.url.path.startswith(
        "/admin"
    ):

        return templates.TemplateResponse(

            request=request,

            name=(
                "admin/errors/500.html"
            ),

            context={

                "admin": None,

                "active_page": "",
            },

            status_code=500,
        )


    # --------------------------------------------------------
    # Development logging
    # --------------------------------------------------------

    print(
        "UNHANDLED ERROR:"
    )

    print(
        type(exc).__name__,
        str(exc),
    )


    # --------------------------------------------------------
    # API response
    # --------------------------------------------------------

    return JSONResponse(

        status_code=500,

        content={

            "detail":
                "Internal server error"
        },
    )