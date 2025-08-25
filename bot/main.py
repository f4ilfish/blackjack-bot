from aiohttp import web

from bot.api.routes import setup_routes
from bot.settings import app_config

if __name__ == "__main__":
    app = web.Application()
    setup_routes(app)
    app["config"] = app_config
    web.run_app(app)
