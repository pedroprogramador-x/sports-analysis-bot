from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    app_name: str = "Sports Analysis Bot v3"
    debug: bool = True
    telegram_token: str = ""
    telegram_chat_id: str = ""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    bsd_api_key: str = ""
    anthropic_api_key: str = ""

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()