from bot.models.card import Card, Rank


class Hand:
    _blackjack_hand_value = 21
    _blackjack_hand_card_count = 2

    def __init__(
        self,
        player_id: int | None = None,
        cards: list[Card] | None = None
    ) -> None:
        self._player_id = player_id
        self._cards = cards if cards is not None else []

    def add_card(self, card: Card) -> None:
        self._cards.append(card)

    def value(self) -> int:
        total = 0
        aces = 0

        for card in self._cards:
            if card.rank == Rank.ACE:
                aces += 1
            total += card.value()

        # Туз может интерпретироваться как 1 вместо 11 в пользу игрока,
        # если его рука больше 21
        while total > Hand._blackjack_hand_value and aces:
            total -= 10
            aces -= 1

        return total

    def is_blackjack(self) -> bool:
        return (
            len(self._cards) == Hand._blackjack_hand_card_count
            and self.value() == Hand._blackjack_hand_value
        )

    def is_bust(self) -> bool:
        return self.value() > Hand._blackjack_hand_value

    def reveal(self) -> None:
        for card in self._cards:
            card.is_hide = False

    def __repr__(self) -> str:
        return f"Hand({self._cards})"
