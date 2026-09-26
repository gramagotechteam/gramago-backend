import time
from collections import defaultdict, deque

from fastapi import (
    HTTPException,
    Request,
    status,
)


class RateLimiter:

    def __init__(
        self,
        limit: int,
        window_seconds: int,
    ):
        self.limit = limit
        self.window_seconds = window_seconds

        self.requests = defaultdict(
            deque
        )


    async def __call__(
        self,
        request: Request,
    ):

        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        now = time.monotonic()

        bucket = self.requests[
            client_ip
        ]

        while (
            bucket
            and now - bucket[0]
            >= self.window_seconds
        ):
            bucket.popleft()

        if len(bucket) >= self.limit:

            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many requests. "
                    "Please try again later."
                ),
            )

        bucket.append(now)