import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError

from dw_blog.exceptions.common import ListException


generic_msg = (
    "Server error! Try again and if problem persist, please contact your admin."
)

def parse_pydantic_msg(body: dict):
    return body[0]["msg"], body[0]["loc"][-1]


class RouteErrorHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as exc:
                exc_message = str(exc) if str(exc) else None
                status_code = 500
                detail = generic_msg if exc_message is None else exc_message
                if isinstance(exc, HTTPException):
                    status_code = exc.status_code
                    detail = exc.detail
                    return JSONResponse(
                        status_code=status_code,
                        content={"detail": f"{detail[0]}"},
                    )
                elif isinstance(exc, ListException):
                    return JSONResponse(
                        status_code=422,
                        content={"detail": [
                            {
                                "status_code": e.status_code,
                                "detail": e.detail,
                            }
                            for e in exc.detail]
                        },
                    )
                elif isinstance(exc, RequestValidationError):
                    error_msg, error_loc = parse_pydantic_msg(exc.errors())
                    status_code = 422
                    detail = f"Validation error: {error_msg}!"
                    return JSONResponse(
                        status_code=status_code,
                        content={"detail": f"{detail}", "location": error_loc},
                    )
                elif isinstance(exc, ValidationError):
                    error_msg = parse_pydantic_msg(exc.errors())
                    status_code = 422
                    detail = f"Validation error: {error_msg}!"
                else:
                    detail = traceback.format_exc()
                return JSONResponse(
                    status_code=status_code,
                    content={"detail": f"{detail}"},
                )

        return custom_route_handler
