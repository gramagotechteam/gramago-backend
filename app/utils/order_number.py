from datetime import datetime, timezone
from uuid import uuid4


def generate_order_number() -> str:

    date_part = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d")

    random_part = (
        uuid4()
        .hex[:8]
        .upper()
    )

    return (
        f"GMG-{date_part}-{random_part}"
    )