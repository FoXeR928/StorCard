from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy import func, DateTime, Uuid
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    type_annotation_map = {uuid.UUID: Uuid(as_uuid=True)}


class TimestampMixin:
    date_create: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), default=datetime.now()
    )
    date_update: Mapped[datetime] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )


from src.database.models.model_users import Users
from src.database.models.model_cards import Cards
from src.database.models.model_configs import Configs
from src.database.models.model_cards_access import CardsAccess
