from sqlalchemy import and_, false, select, true
from sqlalchemy.orm import column_property, relationship

from bot.database.registry import mapper_registry
from bot.database.tables import (
    card_table,
    game_session_player_table,
    game_session_table,
    game_state_table,
    hand_card_table,
    hand_table,
    player_state_table,
    player_table,
)
from bot.game.models.card import Card
from bot.game.models.game import GameSession, GameState
from bot.game.models.hand import Hand
from bot.game.models.player import Dealer, Player, PlayerState


def map_enums() -> None:
    mapper_registry.map_imperatively(
        PlayerState,
        player_state_table,
        properties={
            '_value_': player_state_table.c.state
        }
    )

    mapper_registry.map_imperatively(
        GameState,
        game_state_table,
        properties={
            '_value_': game_state_table.c.state
        }
    )

def map_card() -> None:
    mapper_registry.map_imperatively(
        Card,
        card_table,
        properties={
            'suit': card_table.c.suit,
            'rank': card_table.c.rank,
        }
    )

def map_hand() -> None:
    mapper_registry.map_imperatively(
        Hand,
        hand_table,
        properties={
            'cards': relationship(
                Card,
                secondary=hand_card_table,
                order_by=hand_card_table.c.id,
                collection_class=list
            ),
        }
    )

def map_players() -> None:
    player_state_subquery = (
        select(player_state_table.c.state)
        .where(
            and_(
                player_table.c.id == game_session_player_table.c.player_id,
                game_session_player_table.c.state_id == player_state_table.c.id,
                player_table.c.is_dealer.is_(false())
            )
        )
        .scalar_subquery()
    )

    bet_subquery = (
        select(game_session_player_table.c.bet)
        .where(
            and_(
                player_table.c.id == game_session_player_table.c.player_id,
                player_table.c.is_dealer.is_(false())
            )
        )
        .scalar_subquery()
    )

    mapper_registry.map_imperatively(
        Player,
        player_table,
        properties={
            'user_id': player_table.c.user_id,
            'username': player_table.c.username,
            'balance': player_table.c.balance,
            'bet': column_property(bet_subquery, deferred=False),
            'state': column_property(player_state_subquery, deferred=False),
            'hand': relationship(
                Hand,
                uselist=False,
                primaryjoin=and_(
                    player_table.c.id == game_session_player_table.c.player_id,
                    game_session_player_table.c.id == hand_table.c.game_session_player_id, # noqa: E501
                    player_table.c.is_dealer.is_(false()),
                )
            ),
        },
        primary_key=[player_table.c.id],
        with_polymorphic='*'
    )

    dealer_state_subquery = (
        select(player_state_table.c.state)
        .where(
            and_(
                player_table.c.id == game_session_player_table.c.player_id,
                game_session_player_table.c.state_id == player_state_table.c.id,
                player_table.c.is_dealer.is_(false())
            )
        )
        .scalar_subquery()
    )

    mapper_registry.map_imperatively(
        Dealer,
        player_table,
        properties={
            'user_id': player_table.c.user_id,
            'username': player_table.c.username,
            'state': column_property(dealer_state_subquery, deferred=False),
            'hand': relationship(
                Hand,
                uselist=False,
                primaryjoin=and_(
                    player_table.c.id == game_session_player_table.c.player_id,
                    game_session_player_table.c.id == hand_table.c.game_session_player_id, # noqa: E501
                    player_table.c.is_dealer.is_(true()),
                )
            ),
        },
        primary_key=[player_table.c.id],
        with_polymorphic='*'
    )

def map_game_session() -> None:
    session_state_subquery = (
        select(game_state_table.c.state)
        .where(game_session_table.c.state_id == game_state_table.c.id)
        .scalar_subquery()
    )

    mapper_registry.map_imperatively(
        GameSession,
        game_session_table,
        properties={
            'game_id': game_session_table.c.id,
            'state': column_property(session_state_subquery, deferred=False),
            'players': relationship(
                Player,
                secondary=game_session_player_table,
                primaryjoin=game_session_table.c.id == game_session_player_table.c.game_session_id, # noqa: E501
                secondaryjoin=and_(
                    game_session_player_table.c.player_id == player_table.c.id,
                    player_table.c.is_dealer.is_(false())
                ),
                collection_class=list
            ),
            'dealer': relationship(
                Dealer,
                uselist=False,
                primaryjoin=player_table.c.is_dealer.is_(true())
            ),
            'current_player': relationship(
                Player,
                uselist=False,
                primaryjoin=game_session_table.c.current_player_id == game_session_player_table.c.id # noqa: E501
            ),
        }
    )

def configure_mappers() -> None:
    map_enums()
    map_card()
    map_hand()
    map_players()
    map_game_session()
