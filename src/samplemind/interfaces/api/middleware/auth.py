from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SimpleAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        default_user_id: str = "test_user_v6"
    ):
        super().__init__(app)
        self.default_user_id = default_user_id

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check for X-User-ID header (for testing/future)
        user_id = request.headers.get("X-User-ID", self.default_user_id)

        # Inject user into request state
        request.state.user = {"id": user_id, "role": "admin"}

        response = await call_next(request)
        return response
