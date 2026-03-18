from backend.api.exceptions import (
    BaseAlreadyExistsException,
    BaseInternalServerErrorException,
    BaseUnauthorizedException,
)


class UserExistsException(BaseAlreadyExistsException):
    def __init__(self, user_email: str):
        detail = f"The user {user_email} already exists."
        super().__init__(detail=detail)


class UserCreateInternalErrorException(BaseInternalServerErrorException):
    def __init__(
        self, detail: str = "An internal error occurred while creating the user."
    ):
        super().__init__(detail=detail)


class InvalidCredentialsException(BaseUnauthorizedException):
    def __init__(self, detail: str = "Invalid email or password."):
        super().__init__(detail=detail)


class InvalidTokenException(BaseUnauthorizedException):
    def __init__(self, detail: str = "Invalid authentication token."):
        super().__init__(detail=detail)


class ExpiredTokenException(BaseUnauthorizedException):
    def __init__(self, detail: str = "Authentication token has expired."):
        super().__init__(detail=detail)
