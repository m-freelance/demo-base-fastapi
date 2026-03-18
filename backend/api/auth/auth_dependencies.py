from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.auth.auth_service import AuthService
from backend.api.auth.password_hasher import PasswordHasher
from backend.api.auth.token_service import TokenService
from functools import lru_cache

from backend.api.db.db_dependencies import get_db_session
from backend.api.user.user_dependencies import get_user_repository
from backend.api.user.user_repository import UserRepository


@lru_cache()
def get_password_hasher() -> PasswordHasher:
    """
    get a singleton instance of the PasswordHasher class, which is used to hash and verify user passwords.

    :return: a PasswordHasher instance
    """
    return PasswordHasher()


def get_token_service(request: Request) -> TokenService:
    """
    Get token service from app state. This is a singleton instance that is initialized when the app starts and can be used across the entire application.

    :param request: the FastAPI request object, which provides access to the app state where the token service is stored

    :return: the TokenService instance from the app state
    """
    return request.app.state.token_service


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    db_session: AsyncSession = Depends(get_db_session),
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    """
    FastAPI dependency that provides an instance of the AuthService class, which is responsible for handling user authentication and registration logic.

    :param user_repository: a UserRepository instance that provides methods for interacting with the user data in the database, such as finding users by email and adding new users
    :param password_hasher:  a PasswordHasher instance that provides methods for hashing and verifying user passwords, ensuring that passwords are stored securely in the database
    :param db_session: an AsyncSession instance that provides a database session for performing database operations related to user authentication and registration, such as querying for existing users and adding new users to the database
    :param token_service: a TokenService instance that provides methods for generating and validating JWT tokens, which are used for authenticating users and managing user sessions in the application

    :return: an AuthService instance that can be used in FastAPI routes to handle user authentication and registration logic, such as registering new users and logging in existing users
    """
    return AuthService(
        user_repository=user_repository,
        password_hasher=password_hasher,
        db_session=db_session,
        token_service=token_service,
    )
