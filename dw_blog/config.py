import os
from pathlib import Path

from pydantic import BaseSettings, DirectoryPath, Field


class Settings(BaseSettings):
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    DB_NAME: str = os.getenv("DB_NAME", "fastapi_sqlmodel_db")
    DB_TEST_NAME: str = os.getenv("DB_TEST_NAME", "fastapi_sqlmodel_db_test")
    DB_SERVER: str = os.getenv("DB_SERVER", "db")
    DP_PORT: str = os.getenv("DP_PORT", "5432")
    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DP_PORT}/{DB_NAME}"
    DATABASE_URL_SYNC: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DP_PORT}/{DB_NAME}"
    DATABASE_URL_TEST: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DP_PORT}/{DB_TEST_NAME}"
    DATABASE_URL_TEST_SYNC: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DP_PORT}/{DB_TEST_NAME}"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "this_is_a_secret_number_2137")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    TOKEN_EXPIRATION: int = int(os.getenv("TOKEN_EXPIRATION", 720))
    ROOT_DIR: DirectoryPath = Field(Path(__file__).parent.resolve(), const=True)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")
