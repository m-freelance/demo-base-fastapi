from backend.api.exceptions import BaseInternalServerErrorException


class DatabaseConnectionError(BaseInternalServerErrorException):
    def __init__(self, detail: str = "Failed to connect to the database."):

        super().__init__(detail=detail)


class DatabaseQueryError(BaseInternalServerErrorException):
    def __init__(
        self, detail: str = "An error occurred while executing a database query."
    ):
        super().__init__(detail=detail)


class DatabaseTransactionError(BaseInternalServerErrorException):
    def __init__(
        self, detail: str = "An error occurred during a database transaction."
    ):
        super().__init__(detail=detail)


class DatabaseSessionError(BaseInternalServerErrorException):
    def __init__(
        self, detail: str = "An error occurred while managing database session."
    ):
        super().__init__(detail=detail)


class DatabaseCommitError(BaseInternalServerErrorException):
    def __init__(
        self, detail: str = "An error occurred while committing database transaction."
    ):
        super().__init__(detail=detail)


class DatabaseRollbackError(BaseInternalServerErrorException):
    def __init__(
        self, detail: str = "An error occurred while rolling back database transaction."
    ):
        super().__init__(detail=detail)
