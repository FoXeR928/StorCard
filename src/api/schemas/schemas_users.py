from pydantic import BaseModel


class LoginUpdate(BaseModel):
    login: str


class RegistrationUser(BaseModel):
    login: str
    user_name: Optional[str] = None
    password: str


class UpdateUser(LoginUpdate):
    user_name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = False
