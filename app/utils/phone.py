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