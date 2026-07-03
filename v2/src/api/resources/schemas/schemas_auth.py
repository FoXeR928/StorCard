from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    login: str
    user_name: Optional[str] = None
    is_admin: bool
