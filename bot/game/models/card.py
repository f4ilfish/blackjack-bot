from enum import StrEnum


class Suit(StrEnum):
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'
    SPADES = '♠'

class Rank(StrEnum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'

class Card:
    def __init__(self, suit: Suit, rank: Rank) -> None:
        self.suit = suit
        self.rank = rank

    def value(self) -> int:
        if self.rank in (Rank.JACK, Rank.QUEEN, Rank.KING):
            return 10
        # 1 и 11 для туза учтено в Hand.py
        elif self.rank == Rank.ACE:
            return 11
        return int(str(self.rank.value))

    def __repr__(self) -> str:
        return f'{self.rank.value} {self.suit.value}'
