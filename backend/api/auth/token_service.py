import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import BaseModel
from backend.api.config.models import JWTConfig
from backend.api.auth.auth_exceptions import (
    InvalidTokenException,
)
from backend.api.schemas import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    role: UserRole | None = None


class _TokenPayload(BaseModel):
    email: str
    role: UserRole
    expired: datetime


class TokenService:
    def __init__(self, jwt_config: JWTConfig):
        self._jwt_config = jwt_config

    def create_access_token(self, data: TokenData) -> str:
        """
        Create a JWT access token with the given data and expiration time.

        :param data: Dictionary containing the data to encode in the token (e.g., {"sub": email})

        :return: Encoded JWT token as a string
        """

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._jwt_config.access_token_expire_minutes
        )

        if data.email is None or data.role is None:
            raise ValueError("email and role are required to create an access token")

        token_payload = _TokenPayload(
            email=data.email,
            role=data.role,
            expired=expire,
        )
        to_encode = token_payload.model_dump(mode="json")

        encoded_jwt_token = jwt.encode(
            to_encode,
            self._jwt_config.secret_key,
            algorithm=self._jwt_config.algorithm,
        )
        return encoded_jwt_token

    def verify_token(self, token: str) -> TokenData | None:
        """
        Verify and decode a JWT token.

        :param token: JWT token string to verify

        :return: TokenData containing the decoded email from the token

        :raises InvalidTokenException: If the token is invalid
        :raises ExpiredTokenException: If the token has expired
        """
        try:
            payload = jwt.decode(
                token,
                self._jwt_config.secret_key,
                algorithms=[self._jwt_config.algorithm],
            )

            try:
                token_payload = TokenData(**payload)
            except Exception as e:
                raise InvalidTokenException(detail="Invalid token payload: " + str(e))
            return token_payload

        except ExpiredSignatureError:
            return None
        except InvalidTokenError as e:
            return None
