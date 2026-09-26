# from sqlalchemy.ext.asyncio import (
#     AsyncSession,
#     async_sessionmaker,
#     create_async_engine,
# )

# from app.core.config import settings


# engine = create_async_engine(
#     settings.DATABASE_URL,
#     echo=settings.DEBUG,
#     pool_pre_ping=True,
# )


# AsyncSessionLocal = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )


# async def get_db():
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()






from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


# =========================================================
# DATABASE URL
# =========================================================

database_url = settings.DATABASE_URL


# Railway provides:
# postgresql://user:password@host:port/database
#
# SQLAlchemy async engine with Psycopg 3 needs:
# postgresql+psycopg://user:password@host:port/database

if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

elif database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )


# =========================================================
# ASYNC ENGINE
# =========================================================

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)


# =========================================================
# SESSION FACTORY
# =========================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()