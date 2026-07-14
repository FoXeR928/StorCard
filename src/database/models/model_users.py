import bcrypt
import uuid
from typing import List, Optional
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database.models.model_default import Base, TimestampMixin


class Users(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    login: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    password_hash: Mapped[bytes] = mapped_column(nullable=False)
    user_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)

    cards: Mapped[List["Cards"]] = relationship("Cards", back_populates="owner")
    shared_cards: Mapped[List["CardsAccess"]] = relationship(
        "CardsAccess", back_populates="user"
    )

    def set_password(self, password: str) -> None:
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)

    def check_password(self, password: str) -> bool:
        if self.disabled or not self.password_hash:
            return False
        try:
            return bcrypt.checkpw(password.encode("utf-8"), self.password_hash)
        except Exception:
            return False
