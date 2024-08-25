from typing import Optional

from loguru import logger
from sqlmodel import create_engine
from sqlmodel import select
from sqlmodel import Sequence
from sqlmodel import Session
from sqlmodel import SQLModel

from app.lib import models
from app.lib.settings import settings

engine = create_engine(
    settings.DB_URI,
    echo=True,
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    logger.info("Created tables")


# Dependency
def get_db():
    with Session(engine, expire_on_commit=False) as session:
        yield session


def create_user(conn: Session, user: models.UserCreate) -> models.User:
    db_user = models.User.model_validate(user)
    conn.add(db_user)
    conn.commit()
    conn.refresh(db_user)
    return db_user


def read_users(conn: Session, skip: int = 0, limit: int = 100) -> Sequence[models.User]:
    return conn.exec(select(models.User).offset(skip).limit(limit)).all()


def read_user_by_email(conn: Session, email: str) -> Optional[models.User]:
    return conn.exec(select(models.User).where(models.User.email == email)).first()


def create_activity(conn: Session, activity: models.ActivityCreate) -> models.Activity:
    db_activity = models.Activity.model_validate(activity)
    conn.add(db_activity)
    conn.commit()
    conn.refresh(db_activity)
    return db_activity
