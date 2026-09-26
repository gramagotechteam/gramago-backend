import re
import unicodedata


def generate_slug(value: str) -> str:

    value = unicodedata.normalize(
        "NFKD",
        value,
    )

    value = value.encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    value = value.lower().strip()

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value,
    )

    return value.strip("-")