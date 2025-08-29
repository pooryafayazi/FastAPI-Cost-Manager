# core/config.py
from typing import Final, ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str = "test"
    REDIS_URL: str
    COOKIE_ACCESS_NAME: ClassVar[str] = "access_token"
    COOKIE_REFRESH_NAME: ClassVar[str] = "refresh_token"
    ACCESS_MAX_AGE: ClassVar[int] = 5 * 60
    REFRESH_MAX_AGE: ClassVar[int] = 7 * 24 * 3600
    COOKIE_SECURE: bool = False  # True in Production
    # If there are separate domains for API and front, "none" + secure=True
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: str | None = None
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: list[str] = ["en", "fa"]
    
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "no-replay@example.com"
    MAIL_PORT: int = 25
    MAIL_SERVER: str = "smtp4dev"
    MAIL_FROM_NAME: str = "Admin"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
