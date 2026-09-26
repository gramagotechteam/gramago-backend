import logging

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class StartMessagingError(Exception):
    pass


class StartMessagingService:

    @staticmethod
    async def send_otp(
        *,
        phone: str,
        otp: str,
        idempotency_key: str,
    ) -> str | None:
        """
        Sends an OTP SMS through StartMessaging.

        Returns StartMessaging's OTP request ID
        when available.
        """

        api_key = settings.STARTMESSAGING_API_KEY

        if not api_key:
            raise StartMessagingError(
                "StartMessaging API key is not configured"
            )

        url = (
            f"{settings.STARTMESSAGING_BASE_URL}"
            "/otp/send"
        )

        payload: dict = {
            "phoneNumber": phone,
            "variables": {
                "otp": otp,
                "appName": "GramaGo",
            },
            "idempotencyKey": idempotency_key,
        }

        if settings.STARTMESSAGING_TEMPLATE_ID:
            payload["templateId"] = (
                settings.STARTMESSAGING_TEMPLATE_ID
            )

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        }

        try:
            timeout = httpx.Timeout(
                connect=5.0,
                read=10.0,
                write=10.0,
                pool=5.0,
            )

            async with httpx.AsyncClient(
                timeout=timeout,
            ) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                )

        except httpx.TimeoutException as exc:
            logger.exception(
                "StartMessaging OTP request timed out"
            )

            raise StartMessagingError(
                "OTP service timed out"
            ) from exc

        except httpx.RequestError as exc:
            logger.exception(
                "StartMessaging connection failed"
            )

            raise StartMessagingError(
                "Unable to connect to OTP service"
            ) from exc

        # Do not print API keys or OTP values.
        if response.status_code < 200 or response.status_code >= 300:
            logger.error(
                "StartMessaging OTP failed: status=%s body=%s",
                response.status_code,
                response.text[:500],
            )

            raise StartMessagingError(
                "Unable to send OTP"
            )

        try:
            body = response.json()
        except ValueError as exc:
            raise StartMessagingError(
                "Invalid OTP provider response"
            ) from exc

        if body.get("success") is not True:
            logger.error(
                "StartMessaging unsuccessful response: %s",
                body,
            )

            raise StartMessagingError(
                "Unable to send OTP"
            )

        data = body.get("data") or {}

        otp_request_id = data.get(
            "otpRequestId"
        )

        if otp_request_id is None:
            logger.warning(
                "StartMessaging response did not contain otpRequestId"
            )

            return None

        return str(otp_request_id)