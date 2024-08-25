from os import getenv
from typing import Optional

from loguru import logger
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: Optional[str] = None
    DB_URI: str = "sqlite:///./sql_app.db"

    class Config:
        # Two envs: dev (local) and alpha (production)
        env_type = getenv("PEGASUS_ENV", "")

        env_file = "./.env.prod" if env_type == "alpha" else ".env.dev"
        logger.debug(f"Using env file: {env_file}")


settings = Settings()
