from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
)

metadata = MetaData()


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(32), nullable=True),
    CheckConstraint(
        "username IS NULL OR LENGTH(username) >= 5",
        "ck_username_length"
    ),
)


group = Table(
    "group",
    metadata,
    Column("id", Integer, primary_key=True),
)


group_user = Table(
    "group_user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("group_id", Integer, ForeignKey("group.id")),
    Column("balance", Integer, nullable=False),
    CheckConstraint("balance >= 0", "ck_balance_negative"),
)


game = Table(
    "game",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("created_at", DateTime, nullable=False, default=datetime.now),
    Column("finished_at", DateTime, nullable=True),
    Column("group_id", Integer, ForeignKey("group.id")),
    CheckConstraint(
        "finished_at IS NULL OR finished_at >= created_at",
        "check_finished_after_created_at"
    ),
)

game_player = Table(
    "game_player",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=True),
    Column("game_id", Integer, ForeignKey("game.id")),
    Column("bet", Integer, nullable=True),
    Column("is_dealer", Boolean, nullable=False),
    CheckConstraint(
        "is_dealer = True AND user_id IS NULL AND bet IS NULL",
        "ck_dealer"
    ),
    CheckConstraint(
        "is_dealer = False AND user_id IS NOT NULL AND bet > 0",
        "ck_player"
    ),
)

card = Table(
    "card",
    metadata,
    Column("id", SmallInteger, primary_key=True, autoincrement=True),
    Column("suit", String(1), nullable=False),
    Column("rank", String(2), nullable=False),
    CheckConstraint("LENGTH(suit) = 1", "ck_suit"),
    CheckConstraint("LENGTH(rank) >= 1 AND LENGTH(suit) <= 2", "ck_rank"),
    UniqueConstraint("suit", "rank", "uq_ck_suit_rank"),
)

hand = Table(
    "hand",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("game_player_id", Integer, ForeignKey("game_player.id")),
    Column("card_id", SmallInteger, ForeignKey("card.id")),
    Column("is_hide", Boolean, nullable=False, default=True),
)
