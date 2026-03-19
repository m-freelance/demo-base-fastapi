from fastapi import HTTPException

from backend.api.utils.get_deployment_type import DeploymentType, get_deployment_type


### Base exception classes for the application. ###
class BaseAppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class BaseAlreadyExistsException(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(status_code=409, detail=detail)


class BaseNotFoundException(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)


class BaseUnauthorizedException(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)


class BaseInternalServerErrorException(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)
