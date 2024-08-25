from fastapi import APIRouter
from fastapi import Depends

from ..lib.auth import get_current_user
from ..lib.auth import TokenInfo

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=TokenInfo)
def post_me(
        current_user: TokenInfo = Depends(get_current_user)
):
    """Get the current user (it creates a new user if token is valid and email is verified)"""
    return current_user
