from abc import ABC, abstractmethod
from enum import StrEnum

from bot.game.models.card import Card
from bot.game.models.constants import INIT_TURN_CARD_COUNT, TARGET_DEALER_HAND_VALUE
from bot.game.models.deck import Deck
from bot.game.models.hand import Hand


class PlayerBetResult(StrEnum):
    WIN = 'win'
    LOSE = 'lose'
    PUSH = 'push'


class AbstractPlayer(ABC):
    def __init__(self) -> None:
        self.hand = Hand()
        self.has_stood = False
        self.is_bust = False

    def hit(self, card: Card) -> None:
        self.hand.add_card(card)
        if self.hand.is_bust():
            self.is_bust = True

    def stand(self) -> None:
        self.has_stood = True

    @abstractmethod
    def is_dealer(self) -> bool:
        pass


class Player(AbstractPlayer):
    def __init__(
        self,
        user_id: int,
        username: str,
        balance: int,
    ):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.balance = balance
        self.bet: int = 0

    def is_dealer(self) -> bool:
        return False

    def place_bet(self, amount: int) -> None:
        self.balance -= amount
        self.bet += amount

    def win_bet(self, multiplier: float = 2.0) -> None:
        self.balance += int(self.bet * multiplier)
        self.bet = 0

    def lose_bet(self) -> None:
        self.bet = 0

    def push_bet(self) -> None:
        self.balance += self.bet
        self.bet = 0

    def __repr__(self) -> str:
        return (
            f'{self.username} '
            f'| Balance: {self.balance} '
            f'| Bet: {self.bet} '
            f'| Hand: {self.hand} ({self.hand.value()} points)'
        )


class Dealer(AbstractPlayer):
    def __init__(self) -> None:
        super().__init__()

    def is_dealer(self) -> bool:
        return True

    def play_turn(self, deck: Deck) -> None:
        # Добирать до < 17 по жесткому правилу
        while self.hand.value() < TARGET_DEALER_HAND_VALUE:
            card = deck.draw()
            if not card:
                break
            self.hit(card)

    def __repr__(self) -> str:
        if len(self.hand.cards) == INIT_TURN_CARD_COUNT:
            return f'Dealer | Hand: [{self.hand.cards[0]}, ??]'
        return f'Dealer | Hand: {self.hand} ({self.hand.value()} points)'
