from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Table,
    UniqueConstraint,
    and_,
    false,
    select,
    true,
)
from sqlalchemy.orm import column_property, registry, relationship

from bot.game.models.card import Card
from bot.game.models.game import GameSession, GameState
from bot.game.models.hand import Hand
from bot.game.models.player import Dealer, Player, PlayerState

mapper_registry = registry()
metadata = mapper_registry.metadata

player_state_table = Table(
    'player_state',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('state', String(20), nullable=False),
)

player_table = Table(
    'player',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, nullable=False, unique=True),
    Column('username', String(100), nullable=False),
    Column('balance', Integer, nullable=False, default=1000),
    Column('is_dealer', Boolean, nullable=False, default=False),
)

card_table = Table(
    'card',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('rank', String(2), nullable=False),
    Column('suit', String(1), nullable=False),
    UniqueConstraint('rank', 'suit', name='uq_card_rank_suit'),
)

game_state_table = Table(
    'game_state',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('state', String(20), nullable=False),
)

game_session_table = Table(
    'game_session',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('state_id', ForeignKey('game_state.id'), nullable=False),
    Column('current_player_id', Integer, nullable=True),
)

game_session_player_table = Table(
    'game_session_player',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('game_session_id', ForeignKey('game_session.id'), nullable=False),
    Column('player_id', ForeignKey('player.id'), nullable=False),
    Column('bet', Integer, nullable=False, default=0),
    Column('state_id', ForeignKey('player_state.id'), nullable=False),
    UniqueConstraint(
        'game_session_id',
        'player_id',
        name='uq_game_session_id_player_id'
    ),
)

hand_table = Table(
    'hand',
    metadata,
    Column('id', Integer, primary_key=True),
    Column(
        'game_session_player_id',
        ForeignKey('game_session_player.id'),
        nullable=False
    ),
)

hand_card_table = Table(
    'hand_card',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('hand_id', ForeignKey('hand.id'), nullable=False),
    Column('card_id', ForeignKey('card.id'), nullable=False),
)

ForeignKeyConstraint(
    ['current_player_id'], ['game_session_player.id'],
    table=game_session_table,
    use_alter=True,
    name='fk_game_session_current_player'
)

mapper_registry.map_imperatively(
    PlayerState,
    player_state_table,
    properties={
        'value': player_state_table.c.state
    }
)

mapper_registry.map_imperatively(
    GameState,
    game_state_table,
    properties={
        'value': game_state_table.c.state
    }
)

mapper_registry.map_imperatively(
    Card,
    card_table,
    properties={
        'suit': card_table.c.suit,
        'rank': card_table.c.rank,
    }
)

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
                game_session_player_table.c.id == hand_table.c.game_session_player_id,
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
                game_session_player_table.c.id == hand_table.c.game_session_player_id,
                player_table.c.is_dealer.is_(true()),
            )
        ),
    },
    primary_key=[player_table.c.id],
    with_polymorphic='*'
)

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
