import re

from fastapi import HTTPException, status


def normalize_indian_phone(
    phone: str,
) -> str:
    value = phone.strip()

    value = re.sub(
        r"[\s\-\(\)]",
        "",
        value,
    )

    if value.startswith("+91"):
        number = value[3:]

    elif value.startswith("91") and len(value) == 12:
        number = value[2:]

    else:
        number = value

    if not re.fullmatch(
        r"[6-9]\d{9}",
        number,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Enter a valid Indian mobile number",
        )

    return f"+91{number}"





def format_indian_phone_e164(
    phone: str,
) -> str:

    phone = (
        phone
        .strip()
        .replace(" ", "")
        .replace("-", "")
    )

    if phone.startswith("+91"):
        number = phone[3:]

    elif phone.startswith("91") and len(phone) == 12:
        number = phone[2:]

    elif len(phone) == 10:
        number = phone

    else:
        raise ValueError(
            "Invalid Indian mobile number"
        )

    if (
        len(number) != 10
        or not number.isdigit()
        or number[0] not in "6789"
    ):
        raise ValueError(
            "Invalid Indian mobile number"
        )

    return f"+91{number}"