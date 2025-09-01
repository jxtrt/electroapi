"""Module providing rate limiting middleware for FastAPI applications."""

import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


def get_identifier(request: Request) -> str:
    """Get a unique identifier for the requestor."""
    # no api keys, using IP address
    return request.client.host


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Implements simple rate limiting based on IP address."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(
            lambda: (time.time(), 0)
        )  # Initialize with current time and count 0

    async def dispatch(self, request: Request, call_next):
        """Process incoming requests and enforce rate limits."""
        identifier = get_identifier(request)
        current_time = time.time()

        window_start, count = self.requests[identifier]

        if current_time - window_start > self.window_seconds:
            # Reset the window
            window_start = current_time
            count = 0

        count += 1
        self.requests[identifier] = (window_start, count)

        if count > self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        response = await call_next(request)
        return response
