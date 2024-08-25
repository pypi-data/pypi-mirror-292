from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.lib.db import create_activity
from app.lib.db import get_db
from app.lib.models import ActivityCreate
from app.lib.utils import parse_user_agent

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


class ClickReq(BaseModel):
    button_name: str


@router.post("/click", response_model=None)
async def click(
        *,
        conn: Session = Depends(get_db),
        req: ClickReq,
        request: Request,
):
    ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0]
    browser = parse_user_agent(request.headers.get("User-Agent"))
    create_activity(conn, ActivityCreate(type="click", where=req.button_name, source=ip, browser=browser))
