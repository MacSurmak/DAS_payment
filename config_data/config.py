from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота
    hash: str             # Хеш сохраненного пароля


@dataclass
class Redis:
    user: str
    password: str
    host: str
    port: str


@dataclass
class Config:
    bot: TgBot
    redis: Redis


def load_config(path: str | None) -> Config:

    env: Env = Env()
    env.read_env(path)

    return Config(bot=TgBot(token=env('BOT_TOKEN'),
                            admin_ids=list(map(int, env.list('ADMIN_IDS'))),
                            hash=env('ADMIN_PASSWORD')),
                  redis=Redis(user=env('REDIS_USER'),
                              password=env('REDIS_USER_PASSWORD'),
                              host=env('REDIS_HOST'),
                              port=env('REDIS_PORT')))
