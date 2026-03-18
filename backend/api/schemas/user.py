from backend.api.schemas.base import Base
from uuid import uuid4
from sqlalchemy import String, Column, Integer, Boolean, Enum as saEnum
from enum import Enum, unique


@unique
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    user_uuid = Column(String, default=lambda: str(uuid4()), unique=True, index=True)
    role = Column(
        saEnum(
            UserRole,
            values_callable=lambda t: [str(item.value) for item in t],
            native_enum=False,
        ),
        default=UserRole.USER,
        nullable=False,
    )
