from aiohttp.web import Application

from bot.api.view import index


def setup_routes(app: Application) -> None:
    app.router.add_get("/", index)
