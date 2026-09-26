from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


class EmailService:

    @staticmethod
    async def send_email(
        recipient: str,
        subject: str,
        body: str,
    ) -> None:

        if not settings.SMTP_HOST:
            raise RuntimeError(
                "SMTP_HOST is not configured"
            )

        if not settings.SMTP_FROM_EMAIL:
            raise RuntimeError(
                "SMTP_FROM_EMAIL is not configured"
            )

        message = EmailMessage()

        message["From"] = (
            f"{settings.SMTP_FROM_NAME} "
            f"<{settings.SMTP_FROM_EMAIL}>"
        )

        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=(
                settings.SMTP_USE_TLS
                if not settings.SMTP_USE_SSL
                else False
            ),
            use_tls=settings.SMTP_USE_SSL,
            timeout=30,
        )


    @staticmethod
    async def send_password_reset(
        recipient: str,
        token: str,
    ) -> None:

        subject = "Reset your GramaGo password"

        body = f"""
Hello,

A password reset was requested for your GramaGo account.

Your password reset token is:

{token}

This token will expire in
{settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.

If you did not request this password reset,
you can ignore this email.

GramaGo
"""

        await EmailService.send_email(
            recipient=recipient,
            subject=subject,
            body=body,
        )


    @staticmethod
    async def send_verification_email(
        recipient: str,
        token: str,
    ) -> None:

        subject = "Verify your GramaGo email"

        body = f"""
Welcome to GramaGo!

Please verify your email address.

Your verification token is:

{token}

This token expires in
{settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours.

GramaGo
"""

        await EmailService.send_email(
            recipient=recipient,
            subject=subject,
            body=body,
        )