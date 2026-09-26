import hashlib
import hmac
import secrets
import uuid

from app.core.config import settings


def generate_otp() -> str:
    """
    Cryptographically secure six-digit OTP.
    """

    return f"{secrets.randbelow(1_000_000):06d}"


def generate_challenge_id() -> str:
    """
    Public identifier sent to the client.
    """

    return uuid.uuid4().hex


def generate_idempotency_key() -> str:
    """
    One key per intentional OTP send.
    """

    return str(uuid.uuid4())


def hash_otp(
    *,
    challenge_id: str,
    otp: str,
) -> str:
    """
    Keyed HMAC means a stolen DB alone is not
    enough to brute-force six-digit OTP hashes.
    """

    message = (
        f"{challenge_id}:{otp}"
    ).encode("utf-8")

    secret = settings.OTP_PEPPER.encode(
        "utf-8"
    )

    return hmac.new(
        secret,
        message,
        hashlib.sha256,
    ).hexdigest()


def verify_otp_hash(
    *,
    challenge_id: str,
    otp: str,
    expected_hash: str,
) -> bool:
    actual_hash = hash_otp(
        challenge_id=challenge_id,
        otp=otp,
    )

    return hmac.compare_digest(
        actual_hash,
        expected_hash,
    )