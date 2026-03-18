from backend.api.schemas.base import Base
from uuid import uuid4
from sqlalchemy import String, Integer, Boolean, Enum as saEnum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum, unique


@unique
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_uuid: Mapped[str] = mapped_column(
        String, default=lambda: str(uuid4()), unique=True, index=True
    )
    role: Mapped[UserRole] = mapped_column(
        saEnum(
            UserRole,
            values_callable=lambda t: [str(item.value) for item in t],
            native_enum=False,
        ),
        default=UserRole.USER,
        nullable=False,
    )
