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


class UpdateCard(CardBase):
    name: Optional[str] = None
    about: Optional[str] = None
    code: Optional[str] = None
    code_type: Optional[str] = None
    own: Optional[str] = None


class AddCardAccess(CardBase):
    login: str
