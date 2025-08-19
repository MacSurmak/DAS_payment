from dataclasses import dataclass

from environs import Env
from sqlalchemy.engine.url import URL


@dataclass
class DatabaseConfig:
    """Database connection configuration."""

    url: URL


@dataclass
class TgBot:
    """Telegram bot configuration."""

    token: str
    admin_ids: list[int]
    admin_password: str


@dataclass
class RedisConfig:
    """Redis connection configuration."""

    host: str
    port: int
    user: str
    password: str
    bot_database: int
    middleware_database: int


@dataclass
class Config:
    """Main configuration object."""

    bot: TgBot
    db: DatabaseConfig
    redis: RedisConfig


def load_config(path: str | None = ".env") -> Config:
    """
    Loads configuration from environment variables.

    Args:
        path: Path to the .env file.

    Returns:
        A Config object.
    """
    env = Env()
    env.read_env(path)

    return Config(
        bot=TgBot(
            token=env("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS"))),
            admin_password=env("ADMIN_PASSWORD"),
        ),
        db=DatabaseConfig(
            url=URL.create(
                drivername="postgresql+asyncpg",
                host=env("DB_HOST"),
                port=env.int("DB_PORT"),
                username=env("DB_USER"),
                password=env("DB_PASSWORD"),
                database=env("DATABASE"),
            )
        ),
        redis=RedisConfig(
            host=env("REDIS_HOST"),
            port=env.int("REDIS_PORT"),
            user=env("REDIS_USER"),
            password=env("REDIS_PASSWORD"),
            bot_database=env.int("REDIS_BOT_DATABASE"),
            middleware_database=env.int("REDIS_MIDDLEWARE_DATABASE"),
        ),
    )
