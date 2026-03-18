from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.user import User
from backend.api.user.user_dtos import GetUserResponseDto
from backend.api.user.user_repository import UserRepository


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        db_session: AsyncSession,
    ):
        self._user_repository: UserRepository = user_repository
        self._db_session: AsyncSession = db_session

    async def get_all_users(self, page_params) -> Page[User]:
        """
        Get a list of all users in the database.

        :return: a list of User entities
        """
        users = await self._user_repository.get_all_users(self._db_session, page_params)
        return users

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by their email address.

        :param email: the email address to search for
        :return: the User entity if found, otherwise None
        """
        return await self._user_repository.find_user_by_email(email, self._db_session)
