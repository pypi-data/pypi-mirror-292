from sys import stderr
from sys import stdout

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.api import analytics
from app.api import home
from app.api import users
from app.lib.db import create_db_and_tables
from app.lib.settings import settings

logger.remove(0)
logger.add(stdout, level="DEBUG")
logger.add(stderr, level="ERROR")
logger.add("logs/app.log", level="INFO", rotation="1 day", retention="1 week")

app = FastAPI()

logger.debug(f"Environment: {settings.model_dump()}")


@app.on_event("startup")
async def startup_event():
    create_db_and_tables()


app.mount("/public", StaticFiles(directory="public"), name="public")

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")  # For Nginx

app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(home.router)  # Must be last

origins = [
    # Replace this with your domain
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
