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


class PlayerState(StrEnum):
    BET = 'bet'
    WAIT_TURN = 'wait_turn'
    TURN = 'turn'
    END_TURN = 'end_turn'


class AbstractPlayer(ABC):
    def __init__(
        self,
        user_id: int,
        username: str,
        state: PlayerState,
        hand: Hand | None = None,
    ) -> None:
        self.user_id = user_id
        self.username = username
        self.hand = Hand() if hand is None else hand
        self.state = state

    def is_bust(self) -> bool:
        return self.hand.is_bust()

    def hit(self, card: Card) -> None:
        if self.state == PlayerState.TURN:
            self.hand.add_card(card)
            return None
        return None

    def stand(self) -> None:
        if self.state == PlayerState.TURN:
            self.state = PlayerState.END_TURN

    @abstractmethod
    def is_dealer(self) -> bool:
        pass


class Player(AbstractPlayer):
    def __init__(
        self,
        user_id: int,
        username: str,
        balance: int,
        bet: int = 0,
        state: PlayerState = PlayerState.BET,
        hand: Hand | None = None,
    ):
        super().__init__(user_id, username, state, hand)
        self.balance = balance
        self.bet: int = bet

    def is_dealer(self) -> bool:
        return False

    def place_bet(self, amount: int) -> None:
        if self.state == PlayerState.BET:
            self.balance -= amount
            self.bet += amount
            self.state = PlayerState.WAIT_TURN
            return None
        return None

    def win_bet(self, multiplier: float = 2.0) -> None:
        if self.state == PlayerState.END_TURN:
            self.balance += int(self.bet * multiplier)
            self.bet = 0
            return None
        return None

    def lose_bet(self) -> None:
        if self.state == PlayerState.END_TURN:
            self.balance -= self.bet
            self.bet = 0
            return None
        return None

    def push_bet(self) -> None:
        if self.state == PlayerState.END_TURN:
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
    def __init__(
        self,
        user_id: int = 1,
        username: str = 'Dealer',
        state: PlayerState = PlayerState.WAIT_TURN,
        hand: Hand | None = None,
    ) -> None:
        super().__init__(user_id, username, state, hand)

    def is_dealer(self) -> bool:
        return True

    def play_turn(self, deck: Deck) -> None:
        if self.state == PlayerState.TURN:
            # Добирать до < 17 по жесткому правилу
            while self.hand.value() < TARGET_DEALER_HAND_VALUE:
                card = deck.draw()
                if not card:
                    break
                self.hit(card)
            self.state = PlayerState.END_TURN
            return None
        return None

    def __repr__(self) -> str:
        if len(self.hand.cards) == INIT_TURN_CARD_COUNT:
            return f'{self.username} | Hand: [{self.hand.cards[0]}, ??]'
        return f'{self.username} | Hand: {self.hand} ({self.hand.value()} points)'
