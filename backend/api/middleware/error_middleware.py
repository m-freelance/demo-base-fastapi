import json

from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api.config.models import ErrorMiddlewareConfig
from backend.api.utils.get_logger import get_logger

logger = get_logger(__name__)


class ErrorMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware for consistent error responses.
    """

    _INTERNAL_SERVER_ERROR_MESSAGE = (
        "An unexpected error occurred. Please try again later."
    )

    def __init__(
        self,
        app: FastAPI,
        config: ErrorMiddlewareConfig,
    ) -> None:
        super().__init__(app)
        self._config = config

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        intercept exceptions raised during request processing and return consistent JSON error responses

        :param request: the incoming HTTP request
        :param call_next: the next middleware or route handler to call

        :return: a JSON response with the error message and appropriate HTTP status code
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # Handle both BaseAppException (which inherits from HTTPException) and FastAPI's HTTPException
            return self._create_response(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            return self._create_response(status_code=500, detail=str(e))

    def _create_response(self, status_code: int, detail: str) -> Response:
        """
        create a JSON response with the given status code and error message, and log internal server errors. if
        the status code indicates an internal server error (5xx), log the error details and return a generic error
        message to the client, unless configured to return detailed internal errors.

        :param status_code: the HTTP status code to return in the response
        :param detail: the error message to include in the response body, which may be logged if it's an internal server error

        :return: a JSON response containing the error message and the specified HTTP status code
        """
        if 500 <= status_code < 600:
            logger.error(f"An error occurred: {detail}", exc_info=True)
            detail = (
                detail
                if self._config.return_detailed_internal_errors
                else self._INTERNAL_SERVER_ERROR_MESSAGE
            )
        return Response(
            content=json.dumps({"message": detail}),
            status_code=status_code,
            media_type="application/json",
        )
