from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.auth.auth_dtos import (
    RegisterRequestDto,
    RegisterResponseDto,
    LoginRequestDto,
    LoginResponseDto,
)
from backend.api.auth.auth_exceptions import (
    UserExistsException,
    UserCreateInternalErrorException,
    InvalidCredentialsException,
)
from backend.api.auth.token_service import TokenService, TokenData
from backend.api.user.user_repository import UserRepository
from backend.api.auth.password_hasher import PasswordHasher
from backend.api.schemas import User, UserRole


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        db_session: AsyncSession,
        token_service: TokenService,
    ):
        self._auth_repository: UserRepository = user_repository
        self._password_hasher: PasswordHasher = password_hasher
        self._db_session: AsyncSession = db_session
        self._token_service: TokenService = token_service

    async def add_new_user(self, user: RegisterRequestDto) -> RegisterResponseDto:
        """
        add a new user to the database, if the email is not already taken, and return the created user details

        :param user: the user details to create, including email and password

        :return: a RegisterResponseDto containing the created user's id and email

        :raises UserExistsException: if a user with the given email already exists in the database
        :raises UserCreateInternalErrorException: if there is an internal error during user creation, such as a database error
        """

        encrypted_password = self._password_hasher.encrypt_password(user.password)

        user = User(
            email=str(user.email),
            hashed_password=encrypted_password,
            role=UserRole.USER,
        )

        if await self._auth_repository.find_user_by_email(user.email, self._db_session):
            raise UserExistsException(user.email)

        try:
            result = await self._auth_repository.add_new_user(user, self._db_session)
            await self._db_session.commit()
        except Exception as e:
            raise UserCreateInternalErrorException(detail=str(e))

        response = RegisterResponseDto(
            id=UUID4(result.user_uuid),
            email=result.email,
        )
        return response

    async def login(self, login_request: LoginRequestDto) -> LoginResponseDto:
        """
        Authenticate a user and return a JWT access token.

        :param login_request: the login credentials containing email and password

        :return: a LoginResponseDto containing the access token and token type

        :raises InvalidCredentialsException: if the email or password is incorrect
        """
        user = await self._auth_repository.find_user_by_email(
            login_request.username, self._db_session
        )

        if not user or not self._password_hasher.verify_password(
            login_request.password, user.hashed_password
        ):
            raise InvalidCredentialsException()

        token_data = TokenData(email=user.email, role=user.role)
        # Create JWT token
        access_token = self._token_service.create_access_token(data=token_data)

        return LoginResponseDto(
            access_token=access_token,
            token_type="bearer",
        )
