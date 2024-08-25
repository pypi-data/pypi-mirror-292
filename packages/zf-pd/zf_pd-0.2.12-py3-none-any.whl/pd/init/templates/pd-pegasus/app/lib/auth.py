from fastapi import Depends
from fastapi import HTTPException
from httpx import AsyncClient
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.lib.db import create_user
from app.lib.db import get_db
from app.lib.db import read_user_by_email
from app.lib.errors import ErrAuth
from app.lib.models import UserCreate


class TokenInfo(BaseModel):
    user_id: str
    email: str
    verified: bool = False
    token: str
    expires_in: int


async def get_user(token: str) -> TokenInfo:
    """Verifies the Google OAuth2 token and returns the user data. If expired or invalid, raises 401"""
    async with AsyncClient() as client:
        token_info = await client.get(
            url="https://www.googleapis.com/oauth2/v1/tokeninfo",
            params={"access_token": token}
        )
        if token_info.status_code != 200:
            raise ErrAuth("Invalid token")

        token_data = token_info.json()
        if token_data.get("error"):
            raise ErrAuth("Invalid token")

        if token_data.get("verified_email") is False:
            raise ErrAuth("Unverified email")

        data = token_info.json()
        return TokenInfo(
            user_id=data["user_id"],
            email=data["email"],
            verified=data["verified_email"],
            token=token,
            expires_in=data["expires_in"],
        )


async def get_current_user(
        request: Request,
        conn: Session = Depends(get_db),
) -> TokenInfo:
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Missing token")

    # Assuming the format is "Bearer <token>"
    token = auth_header.split(" ")[1]
    token_data = await get_user(token)

    db_user = read_user_by_email(conn=conn, email=token_data.email)

    if not db_user:
        # Create user if not found in DB (first time login)
        new_user = await get_profile_info(token_data)
        db_user = create_user(conn=conn, user=new_user)

        if not db_user:
            raise ErrAuth("Unregistered")

    # Check if user is deactivated
    if not db_user.is_active:
        logger.debug(f"User is deactivated: {db_user.email}")
        raise ErrAuth("Deactivated")

    return token_data


async def get_profile_info(token_info: TokenInfo) -> UserCreate:
    """Fetches the user's Google Info a UserBase Object. If expired or invalid, raises 401"""
    if not token_info.verified:
        raise ErrAuth("Unverified email")
    if token_info.expires_in < 10:
        raise ErrAuth("Token expired")

    async with AsyncClient() as client:
        user_info = await client.get(
            url="https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
            params={"access_token": token_info.token}
        )
        if user_info.status_code != 200:
            raise ErrAuth("Invalid token")

        user_data = user_info.json()
        if user_data.get("error"):
            raise ErrAuth("Invalid token")

        logger.debug(f"UserInfo: {user_info.json()}")

        return UserCreate(
            id=user_data["id"],
            email=user_data["email"],
            verified=True,
            name=user_data["name"],
            picture=user_data["picture"],
        )
