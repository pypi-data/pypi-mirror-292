# -*- coding: utf-8 -*-
"""Altissimo FastAPI class file."""
import json

from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
# from pydantic import Field
from pydantic import model_validator

from fastapi import Query
from fastapi import Request
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

# pylint: disable=too-few-public-methods


class JSONPrettyPrintMiddleware(BaseHTTPMiddleware):
    """Fast API JSON Pretty Prinut Middleware."""

    def __init__(self, app, excluded_paths: List[str] | None = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        """Pretty print JSON Response."""
        response = await call_next(request)

        # Skip excluded paths and non-streaming responses
        if request.url.path in self.excluded_paths or not isinstance(response, StreamingResponse):
            return response

        # Collect the stream into a single bytes object
        body = b""
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                chunk = chunk.encode()  # Ensure chunk is bytes
            body += chunk

        # Only modify application/json responses
        if response.headers.get("content-type") == "application/json":
            data = json.loads(body.decode())
            pretty_json = json.dumps(
                data,
                ensure_ascii=False,
                allow_nan=False,
                indent=4,
                separators=(", ", ": "),
            ).encode("utf-8")

            # Create a new response with the pretty JSON and original status code
            response.headers["Content-Length"] = str(len(pretty_json))
            return Response(
                content=pretty_json,
                status_code=response.status_code,
                media_type="application/json",
                headers=dict(response.headers),
            )

        return response


class Direction(str, Enum):
    """Altissimo FastAPI Direction class."""
    ASCENDING = "ascending"
    DESCENDING = "descending"


class PaginatedList(BaseModel):
    """Altissimo FastAPI Paginated List class."""
    items: list = []
    next_cursor: str = ""
    previous_cursor: str = ""
    total: Optional[int] = None


class Pagination(BaseModel):
    """Altissimo FastAPI Pagination class."""
    limit: int = Query(default=100)
    next_cursor: str = Query(default="")
    previous_cursor: str = Query(default="")
    order_by: str = Query(default="id")
    direction: Direction = Query(default=Direction.ASCENDING)
    include_total: bool = Query(default=False)

    @model_validator(mode="after")
    def check_cursors(self):
        """Check that only one of next_cursor or prev_cursor is set."""
        if self.next_cursor and self.previous_cursor:
            raise ValueError("Only one of next_cursor or previous_cursor can be set.")
        return self
