import uuid
from typing import Optional, List
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, LargeBinary, UniqueConstraint
from database.models.model_default import Base, TimestampMixin


class Cards(Base, TimestampMixin):
    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    about: Mapped[str] = mapped_column(nullable=True)
    own_login: Mapped[str] = mapped_column(
        ForeignKey("users.login", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    version: Mapped[int] = mapped_column(default=1)
    is_delete: Mapped[bool] = mapped_column(default=False)
    code: Mapped[str] = mapped_column(nullable=False)
    code_type: Mapped[str] = mapped_column(nullable=False)

    owner: Mapped["Users"] = relationship("Users", back_populates="cards")
    shared_access: Mapped[List["CardsAccess"]] = relationship(
        "CardsAccess", back_populates="card", cascade="all,delete-orphan"
    )


class CardsAccess(Base, TimestampMixin):
    __tablename__ = "cards_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_login: Mapped[str] = mapped_column(
        ForeignKey("users.login", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    access_type: Mapped[str] = mapped_column(default="read", nullable=False)

    user: Mapped["Users"] = relationship("Users", back_populates="shared_cards")
    card: Mapped["Cards"] = relationship("Cards", back_populates="shared_access")

    __table_args__ = (
        UniqueConstraint("user_login", "card_id", name="uq_user_card_access"),
    )
