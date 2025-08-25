from enum import StrEnum


class Suit(StrEnum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Rank(StrEnum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

class Card:
    def __init__(
        self,
        suit: Suit,
        rank: Rank,
        oid: int | None = None,
        is_hide: bool = True,
    ) -> None:
        self._suit = suit
        self._rank = rank
        self._oid = oid
        self._is_hide = is_hide

    @property
    def is_hide(self) -> bool:
        return self._is_hide

    @is_hide.setter
    def is_hide(self, value: bool) -> None:
        self._is_hide = value

    @property
    def rank(self) -> Rank:
        return self._rank

    def value(self) -> int:
        if self._rank in (Rank.QUEEN, Rank.KING, Rank.JACK):
            return 10
        # вариант подсчета 1 и 11 для туза учтено в руке
        elif self._rank == Rank.ACE:
            return 11
        return int(str(self._rank.value))

    def __repr__(self) -> str:
        if self._is_hide:
            return "🂠"
        else:
            return f"{self._rank.value} {self._suit.value}"
