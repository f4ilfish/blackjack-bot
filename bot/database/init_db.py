import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy import URL, text  # type-ignore
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.game.models.card import Rank, Suit
from bot.game.models.game import GameState
from bot.game.models.player import PlayerState
from bot.web.config import read_db_config

config_path = (project_root / 'config.yaml')
db_config = read_db_config(config_path.as_posix())

DATABASE_URL = URL.create(
    drivername=db_config.driver,
    username=db_config.user,
    password=db_config.password,
    host=db_config.host,
    port=db_config.port,
    database=db_config.database,
)

async def populate_player_states(session: AsyncSession) -> None:
    for state in PlayerState:
        query = text("""
            INSERT INTO player_state (state)
            VALUES (:state)
            ON CONFLICT DO NOTHING
        """)
        await session.execute(query, {'state': state.value})
    await session.commit()

async def populate_game_states(session: AsyncSession) -> None:
    for state in GameState:
        query = text("""
            INSERT INTO game_state (state)
            VALUES (:state)
            ON CONFLICT DO NOTHING
        """)
        await session.execute(query, {'state': state.value})
    await session.commit()

async def populate_cards(session: AsyncSession) -> None:
    cards_added = 0
    for suit in Suit:
        for rank in Rank:
            query = text("""
                INSERT INTO card (rank, suit)
                VALUES (:rank, :suit)
                ON CONFLICT ON CONSTRAINT uq_card_rank_suit DO NOTHING
            """)
            result = await session.execute(
                query,
                {'rank': rank.value, 'suit': suit.value}
            )
            if result.rowcount > 0:
                cards_added += 1
    await session.commit()

async def create_dealer(session: AsyncSession) -> None:
    query = text("""
        INSERT INTO player (user_id, username, balance, is_dealer)
        VALUES (1, 'Dealer', 0, TRUE)
        ON CONFLICT DO NOTHING
    """)
    await session.execute(query)
    await session.commit()

async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with async_session() as session:
        try:
            await populate_player_states(session)
            await populate_game_states(session)
            await populate_cards(session)
            await create_dealer(session)
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    await engine.dispose()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception:
        sys.exit(1)
