
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     APP_NAME: str = "GramaGo API"
#     APP_ENV: str = "development"
#     DEBUG: bool = True

#     API_V1_PREFIX: str = "/api/v1"

#     DATABASE_URL: str

#     JWT_SECRET_KEY: str
#     JWT_ALGORITHM: str = "HS256"

#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
#     REFRESH_TOKEN_EXPIRE_DAYS: int = 30

#     PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
#     EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

#     CLOUDINARY_CLOUD_NAME: str | None = None
#     CLOUDINARY_API_KEY: str | None = None
#     CLOUDINARY_API_SECRET: str | None = None

#     SMTP_HOST: str | None = None
#     SMTP_PORT: int = 587
#     SMTP_USERNAME: str | None = None
#     SMTP_PASSWORD: str | None = None
#     SMTP_FROM_EMAIL: str | None = None
        
#     SMTP_FROM_EMAIL: str | None = None
#     SMTP_FROM_NAME: str = "GramaGo"

#     SMTP_USE_TLS: bool = True
#     SMTP_USE_SSL: bool = False

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=True,
#         extra="ignore",
#     )


# settings = Settings()









from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    APP_NAME: str = "GramaGo API"

    APP_ENV: str = "development"

    DEBUG: bool = True


    # =========================================================
    # API
    # =========================================================

    API_V1_PREFIX: str = "/api/v1"


    # =========================================================
    # DATABASE
    # =========================================================

    DATABASE_URL: str


    # =========================================================
    # JWT
    # =========================================================

    JWT_SECRET_KEY: str

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24


    # =========================================================
    # CLOUDINARY
    # =========================================================

    CLOUDINARY_CLOUD_NAME: str | None = None

    CLOUDINARY_API_KEY: str | None = None

    CLOUDINARY_API_SECRET: str | None = None


    # =========================================================
    # SMTP
    # =========================================================

    SMTP_HOST: str | None = None

    SMTP_PORT: int = 587

    SMTP_USERNAME: str | None = None

    SMTP_PASSWORD: str | None = None

    SMTP_FROM_EMAIL: str | None = None

    SMTP_FROM_NAME: str = "GramaGo"

    SMTP_USE_TLS: bool = True

    SMTP_USE_SSL: bool = False




    # =========================================================
    # STARTMESSAGING OTP
    # =========================================================

    # STARTMESSAGING_API_KEY: str | None = None

    # STARTMESSAGING_BASE_URL: str = (
    #     "https://api.startmessaging.com"
    # )

    # OTP_EXPIRE_SECONDS: int = 300

    # OTP_RESEND_SECONDS: int = 30
    # =========================================================
    # STARTMESSAGING
    # =========================================================

    STARTMESSAGING_API_KEY: str | None = None

    STARTMESSAGING_BASE_URL: str = (
        "https://api.startmessaging.com"
    )

    STARTMESSAGING_TEMPLATE_ID: str | None = None


    # =========================================================
    # OTP SECURITY
    # =========================================================

    OTP_EXPIRE_SECONDS: int = 300

    OTP_RESEND_SECONDS: int = 30

    OTP_MAX_ATTEMPTS: int = 5

    OTP_PEPPER: str
    # =========================================================
    # FIREBASE
    # =========================================================

    FIREBASE_CREDENTIALS_PATH: str | None = None


    # =========================================================
    # PYDANTIC SETTINGS
    # =========================================================

    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

        case_sensitive=True,

        extra="ignore",
    )


settings = Settings()