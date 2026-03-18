from pydantic import Field, UUID4

from backend.api.schemas import UserRole, User
from backend.api.utils.dtos import DTOBase


class UserDto(DTOBase): ...


class GetUserResponseDto(UserDto):
    user_uuid: UUID4 = Field(..., description="Unique identifier of the user")
    email: str = Field(..., description="User's email address")
    is_active: bool = Field(..., description="Whether the user is active")
    role: UserRole = Field(..., description="User's role")
