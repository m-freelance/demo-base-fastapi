from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.api.auth.token_service import TokenData, TokenService
from backend.api.config.models import AuthMiddlewareConfig, JWTConfig, PathAccessConfig
from backend.api.schemas.user import UserRole


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Role-based authentication middleware.

    Checks if the request path matches any configured path_access entries.
    If matched, validates the JWT token and checks if the user's role is allowed.
    If not matched, the path is considered public and allows access to anyone.

    Stores the authenticated user's token data in request.state.user_token_data
    """

    def __init__(
        self, app: FastAPI, config: AuthMiddlewareConfig, jwt_config: JWTConfig
    ):
        super().__init__(app)
        self._config: AuthMiddlewareConfig = config
        self._token_service = TokenService(jwt_config=jwt_config)

    async def dispatch(self, request: Request, call_next):
        """
        intercept incoming requests, check if the path and method are protected, and if so, validate the
        JWT token and user role before allowing access to the route handler.

        :param request: the incoming HTTP request to be processed by the middleware
        :param call_next: a function that, when called, will pass the request to the next middleware or route handler in the processing chain, allowing the request to continue through the application if authentication and authorization checks pass successfully

        :return: a JSON response with an appropriate error message and status code if authentication or authorization fails, or the response from the next middleware or route handler if access is granted
        """
        current_path = request.url.path
        current_method = request.method

        # initialize request.state.user_token_data to None
        request.state.user_token_data = None

        # try to extract and verify token for all requests
        token = self._extract_token_from_header(request)
        if token is not None:
            token_data: TokenData | None = self._token_service.verify_token(token)
            if token_data is not None:
                request.state.user_token_data = token_data

        # find matching path access config using prefix matching
        matching_config = self._find_matching_path_config(current_path)

        # if no matching config, path is public - allow access
        if matching_config is None:
            return await call_next(request)

        # check if the HTTP method is protected for this path
        if current_method not in [m.value for m in matching_config.methods]:
            # method not in configured methods, allow access
            return await call_next(request)

        # path and method are protected - require authentication
        if token is None:
            return JSONResponse(
                status_code=401, content={"detail": "Authentication required"}
            )

        # use token_data from request.state (already verified above)
        token_data = request.state.user_token_data
        if token_data is None:
            return JSONResponse(
                status_code=401, content={"detail": "Invalid or expired token"}
            )

        # check if user's role is allowed
        if not self._is_role_allowed(token_data.role, matching_config.allowed_roles):
            return JSONResponse(
                status_code=401, content={"detail": "Insufficient permissions"}
            )

        # proceed with the request processing
        response = await call_next(request)
        return response

    def _find_matching_path_config(self, request_path: str) -> PathAccessConfig | None:
        """
        Find a matching PathAccessConfig for the given request path.

        :param request_path: The request URL path
        :return: Matching PathAccessConfig or None if path is public
        """
        for path_config in self._config.path_access:
            if request_path.startswith(path_config.path):
                return path_config
        return None

    def _extract_token_from_header(self, request: Request) -> str | None:
        """
        Extract JWT token from Authorization header.

        :param request: The incoming request
        :return: Token string or None if not present
        """
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            return None

        # Expected format: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    def _is_role_allowed(
        self, user_role: UserRole | None, allowed_roles: list[UserRole]
    ) -> bool:
        """
        Check if the user's role is in the allowed roles list.

        :param user_role: The user's role from the token
        :param allowed_roles: List of allowed roles for this path
        :return: True if allowed, False otherwise
        """
        if user_role is None:
            return False
        return user_role in allowed_roles
