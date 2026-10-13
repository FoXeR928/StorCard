from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    login: str
    user_name: Optional[str] = None
    is_admin: bool
