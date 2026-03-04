from pydantic import BaseModel
from typing import Optional


class LoginUpdate(BaseModel):
    login: str


class RegistrationUser(BaseModel):
    login: str
    user_name: Optional[str] = None
    password: str


class UpdatePasswordUser(LoginUpdate):
    password: str


class UpdateUser(LoginUpdate):
    user_name: Optional[str] = None
    is_admin: Optional[bool] = False
