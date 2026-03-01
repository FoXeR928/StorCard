import uuid
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.database.base import Base, TimestampMixin


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

    user: Mapped["Users"] = relationship("Users", back_populates="shared_cards")
    card: Mapped["Cards"] = relationship("Cards", back_populates="shared_access")

    __table_args__ = (
        UniqueConstraint("user_login", "card_id", name="uq_user_card_access"),
    )
