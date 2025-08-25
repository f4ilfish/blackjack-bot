import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class DatabaseConfig:
    driver_name: str | None
    username: str | None
    password: str | None
    host: str | None
    port: str | None
    database: str | None

    def get_connection_url(self) -> str:
        return (
            f"{self.driver_name}://"
            f"{self.username}:{self.password}@"
            f"{self.host}:{self.port}/"
            f"{self.database}"
        )


@dataclass(frozen=True)
class BotConfig:
    token: str | None


@dataclass(frozen=True)
class Config:
    database: DatabaseConfig
    bot: BotConfig


def get_config(env_name: str) -> Config:
    load_dotenv(env_name)
    bot_config = BotConfig(token=os.getenv("BOT_TOKEN"))
    database_config = DatabaseConfig(
        driver_name=os.getenv("POSTGRES_DRIVER"),
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
    )
    return Config(database=database_config, bot=bot_config)

app_config = get_config(".env")
