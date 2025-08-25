from abc import ABC, abstractmethod

from bot.models.card import Card
from bot.models.deck import Deck
from bot.models.hand import Hand


class AbstractPlayer(ABC):
    def __init__(
        self,
        game_id: int,
        oid: int | None = None,
    ) -> None:
        self._oid = oid
        self._game_id = game_id
        self.hand: Hand | None = None

    @property
    @abstractmethod
    def is_dealer(self) -> bool:
        pass

    def add_hand(self, hand: Hand) -> None:
        if self.hand is not None:
            raise Exception(f"Player {self._oid} already has a hand")
        self.hand = hand


class Player(AbstractPlayer):
    def __init__(
        self,
        game_id: int,
        user_id: int,
        balance: int,
        oid: int | None = None,
        bet: int = 0,
    ):
        super().__init__(game_id, oid)
        self._user_id = user_id
        self._balance = balance
        self._bet = bet
        self._is_dealer = False

    @property
    def is_dealer(self) -> bool:
        return self._is_dealer

    @property
    def bet(self) -> int:
        return self._bet

    def place_bet(self, amount: int) -> None:
        if amount <= 0:
            raise Exception(
                f"Player's {self._oid} bet amount must be positive."
            )
        if amount > self._balance:
            raise Exception(
                f"Player {self._oid} has not enough balance "
                f"for bet with such amount."
            )
        self._bet += amount

    def hit(self, card: Card) -> None:
        if self.hand is None:
            raise Exception(f"Player {self._oid} has no hand.")
        self.hand.add_card(card)

    def double_down(self, card: Card) -> None:
        if self.hand is None:
            raise Exception(f"Player {self._oid} has no hand.")
        double_bet = self._bet * 2
        if double_bet > self._balance:
            raise Exception(
                f"Player {self._oid} has not enough balance for double bet."
            )
        self._bet = double_bet
        self.hand.add_card(card)

    def win_bet(self, multiplier: int = 2) -> None:
        self._balance += self._bet * multiplier

    def lose_bet(self) -> None:
        self._balance -= self._bet

    def push_bet(self) -> None:
        self._balance += self._bet

    def __repr__(self) -> str:
        hand_value = self.hand.value() if self.hand is not None else None
        return (
            f"Player: {self._oid} | "
            f"Balance: {self._balance} | "
            f"Bet: {self._bet} | "
            f"Hand: {self.hand} ({hand_value} points)"
        )


class Dealer(AbstractPlayer):
    _target_dealer_hand_value = 17

    def __init__(
        self,
        game_id: int,
        oid: int | None = None,
    ) -> None:
        super().__init__(game_id, oid)
        self._is_dealer = True

    @property
    def is_dealer(self) -> bool:
        return self._is_dealer

    def turn(self, deck: Deck) -> None:
        if self.hand is None:
            raise Exception(f"Player {self._oid} has no hand.")
        self.hand.reveal()
        while self.hand.value() < Dealer._target_dealer_hand_value:
            card = deck.draw()
            card.is_hide = False
            self.hand.add_card(card)

    def __repr__(self) -> str:
        hand_value = self.hand.value() if self.hand is not None else None
        return f"Dealer: {self._oid} | Hand: {self.hand} ({hand_value} points)"
