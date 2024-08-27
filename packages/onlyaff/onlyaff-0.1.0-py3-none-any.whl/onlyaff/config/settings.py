from pydantic import AnyHttpUrl, Field, MongoDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Base(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class DatabaseSettings(Base):
    DATABASE_URL: MongoDsn = Field(default=None)


class RedisSettings(Base):
    REDIS_URL: RedisDsn = Field(default=None)


class AuthSettings(Base):
    JWKS_URL: AnyHttpUrl = Field(default=None)
    CLERK_USER_CACHE_TTL: int = Field(default=60)


class ClerkSettings(Base):
    CLERK_BACKEND_API_URL: AnyHttpUrl = Field(default=None)
    CLERK_BACKEND_API_KEY: str = Field(default=None)
