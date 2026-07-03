from sqlalchemy.orm import mapped_column, Mapped
from src.database.base import Base, TimestampMixin


class Configs(Base, TimestampMixin):
    __tablename__ = "configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    about: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
    input_format: Mapped[str] = mapped_column(nullable=False, default="text")
