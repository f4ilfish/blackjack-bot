from dataclasses import dataclass
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from bot.web.app import BlackJackApp

@dataclass
class DatabaseConfig:
    host: str = 'localhost'
    port: int = 5432
    user: str = 'postgres'
    password: str = 'postgres'
    database: str = 'postgres'

@dataclass
class BotConfig:
    token: str

@dataclass
class Config:
    database: DatabaseConfig
    bot: BotConfig

def setup_config(app: 'BlackJackApp', config_path: str) -> None:
    with open(config_path) as f:
        raw_config = yaml.safe_load(f)
        app.config = Config(
            database=DatabaseConfig(**raw_config['database']),
            bot=BotConfig(**raw_config['bot']),
        )
