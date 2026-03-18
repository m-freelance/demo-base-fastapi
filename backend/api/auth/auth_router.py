from fastapi import APIRouter, Depends

from backend.api.auth.auth_dependencies import get_auth_service
from backend.api.auth.auth_dtos import (
    RegisterRequestDto,
    RegisterResponseDto,
    LoginResponseDto,
    LoginRequestDto,
)
from backend.api.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponseDto,
    status_code=201,
    summary="Register a new user",
    description="Endpoint to register a new user with email and password.",
    responses={
        201: {
            "description": "User registered successfully",
        },
        409: {"description": "User already exists"},
        500: {
            "description": "Internal server error during user creation",
        },
    },
)
async def register_user(
    register_request: RegisterRequestDto,
    auth_service=Depends(get_auth_service),
) -> RegisterResponseDto:
    """
    Register a new user with email and password.
    """
    return await auth_service.add_new_user(user=register_request)


@router.post(
    "/login",
    summary="Login user",
    response_model=LoginResponseDto,
    description="Endpoint to login a user",
)
async def login_user(
    login_request: LoginRequestDto = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Authenticate user and return JWT access token.
    """
    return await auth_service.login(login_request)
