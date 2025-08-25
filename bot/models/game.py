from datetime import datetime

from bot.models.deck import Deck
from bot.models.player import Dealer, Player


class Game:
    _max_players = 7
    _deal_card_count = 2

    def __init__(
        self,
        group_id: int,
        oid: int | None = None,
        created_at: datetime | None = None,
        finished_at: datetime | None = None,
    ):
        self._oid = oid
        self._group_id = group_id
        self._created_at = created_at if created_at is not None else datetime.now()
        self._finished_at = finished_at
        self._players: list[Player] = []
        self._dealer: Dealer | None = None
        self._deck: Deck | None = None


    def add_player(self, player: Player) -> None:
        if len(self._players) == Game._max_players:
            raise Exception(
                f"Can't add more players to the game {self._oid}. "
                f"Count of players is already {Game._max_players}"
            )
        self._players.append(player)

    def add_dealer(self, dealer: Dealer) -> None:
        if self._dealer is not None:
            raise Exception(
                f"Dealer has already been added in game {self._oid}"
            )
        self._dealer = dealer

    def add_deck(self, deck: Deck) -> None:
        if self._deck is not None:
            raise Exception(f"Deck has already been added in game {self._oid}")
        self._deck = deck

    def is_all_bets_placed(self) -> bool:
        if not self._players:
            raise Exception(f"No players in the game {self._oid}")
        return all(player.bet > 0 for player in self._players)

    def deal(self) -> None:
        if (
            self._deck is None
            or self._dealer is None
            or not self.is_all_bets_placed()
            or any(player.hand is None for player in self._players)
        ):
            raise Exception(
                f"To deal game {self._oid} must contain dealer, deck "
                "and players with hands and placed bets."
            )
        for i in range(Game._deal_card_count):
            for player in self._players:
                card = self._deck.draw()
                card.is_hide = False
                player.hand.add_card(card) # type: ignore[union-attr]
            card = self._deck.draw()
            # Скрываем только первую карту дилера
            card.is_hide = i == 0
            self._dealer.hand.add_card(card) # type: ignore[union-attr]
