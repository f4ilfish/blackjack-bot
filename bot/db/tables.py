from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Table,
    UniqueConstraint,
)

from bot.db.registry import metadata

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
