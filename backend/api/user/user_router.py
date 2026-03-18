from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from backend.api.auth.token_service import oauth2_scheme
from backend.api.schemas.user import User
from backend.api.user.user_dependencies import get_user_service, get_current_user_info
from backend.api.user.user_dtos import GetUserResponseDto
from backend.api.user.user_service import UserService

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(oauth2_scheme)]
)


@router.get(
    "/me",
    response_model=GetUserResponseDto,
    summary="Get current user",
    description="Protected endpoint to get the current authenticated user's information",
    responses={
        200: {
            "description": "Current user information retrieved successfully",
        },
        401: {"description": "Invalid or missing authentication token"},
    },
)
async def get_me(
    current_user: User = Depends(get_current_user_info),
):
    """
    Get the current authenticated user's information.
    Requires a valid JWT token in the Authorization header.
    """
    return current_user


@router.get(
    "",
    response_model=Page[GetUserResponseDto],
    summary="Get all users",
    description="Protected endpoint to get a list of all users in the database",
    responses={
        200: {
            "description": "List of users retrieved successfully",
        },
        401: {"description": "Invalid or missing authentication token"},
    },
)
async def get_all_users(
    user_service: UserService = Depends(get_user_service),
    page_params: Params = Depends(),
):
    """
    Get a list of all users in the database.
    """
    users = await user_service.get_all_users(page_params)
    return users
