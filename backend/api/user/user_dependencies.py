from functools import lru_cache

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.auth.token_service import TokenData, oauth2_scheme
from backend.api.db.db_dependencies import get_db_session
from backend.api.schemas import User
from backend.api.user.user_repository import UserRepository
from backend.api.user.user_service import UserService


def get_user_repository() -> UserRepository:
    """
    get a new instance of the UserRepository class, which provides methods for interacting with the user data in the database
    """
    return UserRepository()


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    db_session: AsyncSession = Depends(get_db_session),
) -> UserService:
    """
    FastAPI dependency that provides an instance of the UserService class, which is responsible for handling user-related business logic and interactions with the user repository.

    :param user_repository: a UserRepository instance that provides methods for interacting with the user data in the database, such as finding users by email and adding new users
    :param db_session: an AsyncSession instance that provides a database session for performing database operations related to user management, such as querying for existing users and adding new users to the database

    :return: a UserService instance that can be used in FastAPI routes to handle user-related business logic and interactions with the user repository, such as retrieving user information and managing user accounts
    """

    return UserService(
        user_repository=user_repository,
        db_session=db_session,
    )


async def get_current_user_info(
    request: Request,
    user_repository: UserRepository = Depends(get_user_repository),
    db_session: AsyncSession = Depends(get_db_session),
    _token: str = Depends(oauth2_scheme),  # required for OpenAPI Authorize button
) -> User | None:
    """
    Dependency to get the current user's information from request state.

    Note: Authentication is handled by the auth middleware, which stores token data in request.state.

    :param request: The incoming request
    :param user_repository: User repository instance
    :param db_session: Database session
    :param _token : The JWT token from the Authorization header (used for OpenAPI docs, not for actual auth logic)
    :return: The User object or None if user not authenticated
    """
    token_data: TokenData | None = getattr(request.state, "user_token_data", None)
    if token_data is None or token_data.email is None:
        return None

    user = await user_repository.find_user_by_email(token_data.email, db_session)
    return user
