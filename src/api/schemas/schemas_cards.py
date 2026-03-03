import uuid
from typing import Optional
from pydantic import BaseModel


class CardBase(BaseModel):
    id: uuid.UUID


class AddCard(BaseModel):
    name: str
    about: Optional[str] = None
    code: str
    code_type: str


class UpdateCardName(CardBase):
    name: str


class UpdateCardAbout(CardBase):
    about: str


class UpdateCardCode(CardBase):
    code: str
    code_type: str


class UpdateCardOwn(CardBase):
    own: str


class AddCardAccess(CardBase):
    login: str
