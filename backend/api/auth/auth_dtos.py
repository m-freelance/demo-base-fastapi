from typing import Annotated

from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm

from backend.api.utils.dtos import DTOBase
from pydantic import Field, UUID4, EmailStr


class AuthDto(DTOBase): ...


class LoginRequestDto(OAuth2PasswordRequestForm):
    username: Annotated[str, Form(description="User's email address")]
    password: Annotated[str, Form(min_length=8, description="User's password")]
    grant_type: Annotated[str | None, Form(pattern="password")] = None
    scope: Annotated[str, Form()] = ""
    client_id: Annotated[str | None, Form()] = None
    client_secret: Annotated[str | None, Form()] = None


class LoginResponseDto(AuthDto):
    access_token: str = Field(..., alias="access_token", description="JWT access token")
    token_type: str = Field(
        ..., alias="token_type", description="Type of the token, typically 'bearer'"
    )


class RegisterRequestDto(AuthDto):
    email: EmailStr = Field(..., min_length=8, description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")


class RegisterResponseDto(AuthDto):
    id: UUID4 = Field(..., description="Unique identifier of the user")
    email: str = Field(..., description="User's email address")
