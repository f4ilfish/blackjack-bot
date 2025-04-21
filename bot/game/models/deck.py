import random

from bot.game.models.card import Card, Rank, Suit


class Deck:
    def __init__(self, cards: list[Card] | None = None) -> None:
        self.cards = [
            Card(suit, rank)
            for suit in Suit
            for rank in Rank
        ] if cards is None else cards
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        return self.cards.pop() if self.cards else None
