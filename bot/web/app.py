from aiohttp.web import Application

from bot.database.database import Database, setup_database
from bot.web.config import Config, setup_config
from bot.web.logger import setup_logging


class BlackJackApp(Application): # type: ignore
    config: Config | None = None
    database: Database | None = None

app = BlackJackApp()

def setup_app(config_path: str) -> BlackJackApp:
    setup_logging(app)
    setup_config(app, config_path)
    setup_database(app)
    return app
