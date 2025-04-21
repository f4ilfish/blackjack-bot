from typing import TYPE_CHECKING

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    from bot.web.app import BlackJackApp

class Database:
    def __init__(self, app: 'BlackJackApp') -> None:
        self.app = app
        self.engine: AsyncEngine | None = None
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        self.engine = create_async_engine(
            URL.create(
                drivername='postgresql+asyncpg',
                host=self.app.config.database.host,  # type: ignore
                port=self.app.config.database.port, # type: ignore
                username=self.app.config.database.user, # type: ignore
                password=self.app.config.database.password, # type: ignore
                database=self.app.config.database.database, # type: ignore
            ),
            echo=True,
        )
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def disconnect(self) -> None:
        if self.session:
            async with self.session() as session:
                await session.close()


def setup_database(app: 'BlackJackApp') -> None:
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
