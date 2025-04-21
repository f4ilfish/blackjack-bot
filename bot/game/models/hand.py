from bot.game.models.card import Card, Rank
from bot.game.models.constants import BLACK_JACK_HAND_VALUE, INIT_TURN_CARD_COUNT


class Hand:
    def __init__(self, cards: list[Card] | None = None) -> None:
        self.cards = cards or []

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def value(self) -> int:
        total = 0
        aces = 0

        for card in self.cards:
            if card.rank == Rank.ACE:
                aces += 1
            total += card.value()

        # Туз может интерпретироваться и как 11 и как 1
        while total > BLACK_JACK_HAND_VALUE and aces:
            total -= 10
            aces -= 1

        return total

    def is_blackjack(self) -> bool:
        return (
            self.value() == BLACK_JACK_HAND_VALUE
            and len(self.cards) == INIT_TURN_CARD_COUNT
        )

    def is_bust(self) -> bool:
        return self.value() > BLACK_JACK_HAND_VALUE

    def __repr__(self) -> str:
        return f'Hand({self.cards})'
