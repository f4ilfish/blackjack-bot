import random

from bot.models.card import Card, Rank, Suit


class Deck:
    def __init__(
        self,
        game_id: int | None = None,
        cards: list[Card] | None = None
    ) -> None:
        self._game_id = game_id
        if cards is None:
            cards = [
                Card(suit, rank)
                for suit in Suit
                for rank in Rank
            ]
        self._cards = cards
        random.shuffle(cards)

    def draw(self) -> Card:
        if not self._cards:
            raise Exception(
                f"Can't draw a card from game's {self._game_id} deck. "
                f"Deck is empty."
            )
        return self._cards.pop()
