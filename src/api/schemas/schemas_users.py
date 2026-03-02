from pydantic import BaseModel


class LoginUpdate(BaseModel):
    login: str


class RegistrationUser(BaseModel):
    login: str
    user_name: str
    password: str


class UpdatePassword(LoginUpdate):
    password: str


class UpdateRole(LoginUpdate):
    is_admin: bool = False
