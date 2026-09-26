import asyncio

from app.services.email_service import (
    EmailService,
)

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # go up to gramago-backend
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


async def main():

    await EmailService.send_email(
        recipient="akulashivaakulashiva@gmail.com",
        subject="GramaGo SMTP Test",
        body=(
            "SMTP is working successfully "
            "for GramaGo."
        ),
    )

    print(
        "Email sent successfully"
    )


asyncio.run(main())