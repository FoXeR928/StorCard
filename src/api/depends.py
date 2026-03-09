from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from src.core.security import decode_access_token
from src.database.repository.repo_auth import get_user_by_login


class OAuth2CookieStack(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        header_auth = request.headers.get("Authorization")
        if header_auth:
            return await super().__call__(request)
        return request.cookies.get("token")


oauth2_scheme = OAuth2CookieStack(tokenUrl="/v1/auth/login", auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(401, "Not authenticated")

    login = decode_access_token(token)
    if not login:
        raise HTTPException(401, "Token invalid or expired")

    user = get_user_by_login(login)
    if not user:
        raise HTTPException(404, "User not found")
    return user
