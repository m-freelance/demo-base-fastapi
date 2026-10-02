from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel

from backend.api.auth.auth_exceptions import InvalidTokenException
from backend.api.config.models import JWTConfig
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


class TokenService:
    def __init__(self, jwt_config: JWTConfig):
        self._jwt_config = jwt_config

    def create_access_token(self, data: TokenData) -> str:
        """
        Create a JWT access token with the given data and expiration time.

        :param data: Dictionary containing the data to encode in the token (e.g., {"sub": email})

        :return: Encoded JWT token as a string
        """

        if data.email is None or data.role is None:
            raise ValueError("email and role are required to create an access token")

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._jwt_config.access_token_expire_minutes
        )

        token_payload = _TokenPayload(
            email=data.email,
            role=data.role,
        )
        # "exp" is the standard JWT claim name PyJWT checks on decode.
        to_encode = token_payload.model_dump(mode="json")
        to_encode["exp"] = expire

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

        :return: TokenData with the decoded email and role, or None if the
            token is invalid, tampered, or expired

        :raises InvalidTokenException: If the token is well-formed and signed
            correctly but its payload is missing required fields
        """
        try:
            payload = jwt.decode(
                token,
                self._jwt_config.secret_key,
                algorithms=[self._jwt_config.algorithm],
                options={"require": ["exp"]},
            )
        except ExpiredSignatureError:
            return None
        except InvalidTokenError:
            # covers a missing exp claim too, PyJWT raises MissingRequiredClaimError,
            # a subclass of InvalidTokenError, when a required claim is absent
            return None

        try:
            token_payload = _TokenPayload(**payload)
        except Exception as e:
            raise InvalidTokenException(detail="Invalid token payload: " + str(e))

        return TokenData(email=token_payload.email, role=token_payload.role)
