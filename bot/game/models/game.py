import random
from enum import Enum

from bot.game.models.constants import INIT_TURN_CARD_COUNT, MAX_PLAYERS
from bot.game.models.deck import Deck
from bot.game.models.player import Dealer, Player, PlayerBetResult


class GameState(Enum):
    WAITING_FOR_PLAYERS = 'waiting'
    WAITING_FOR_BETS = 'waiting_for_bets'
    PLAYER_TURN = 'player_turn'
    DEALER_TURN = 'dealer_turn'
    FINISHED = 'finished'


class GameSession:
    def __init__(self, game_id: int):
        self.game_id = game_id
        self.deck = Deck()
        self.players: list[Player] = []
        self.dealer = Dealer()
        self.state = GameState.WAITING_FOR_PLAYERS
        self.current_player_index = 0

    def add_player(self, player: Player) -> None:
        if self.state != GameState.WAITING_FOR_PLAYERS:
            raise Exception('Cannot join after game has started')
        if len(self.players) == MAX_PLAYERS:
            raise Exception('Too many players')
        self.players.append(player)

    def start_betting_phase(self) -> None:
        if not self.players:
            raise Exception('No players in game')
        self.state = GameState.WAITING_FOR_BETS

    def all_bets_placed(self) -> bool:
        return all(player.bet > 0 for player in self.players)

    def start_game(self) -> None:
        if self.state != GameState.WAITING_FOR_BETS:
            raise Exception('Must be in betting phase to start game')
        if not self.all_bets_placed():
            raise Exception('All players must place bets')

        self.state = GameState.PLAYER_TURN

        # При первой раздаче карт на 7 игроков точно хватит
        for _ in range(INIT_TURN_CARD_COUNT):
            for player in self.players:
                player.hit(self.deck.draw())  # type: ignore
            self.dealer.hit(self.deck.draw()) # type: ignore

        # Дополнительный элемент случайности
        random.shuffle(self.players)

    def current_player(self) -> Player | None:
        if self.state != GameState.PLAYER_TURN:
            return None
        if self.current_player_index >= len(self.players):
            return None
        return self.players[self.current_player_index]

    def player_action_hit(self) -> None:
        player = self.current_player()
        if not player:
            raise Exception('No active player')
        card = self.deck.draw()
        if not card:
            self.state = GameState.FINISHED
            return
        player.hit(card)
        if player.is_bust:
            self.next_turn()

    def player_action_stand(self) -> None:
        player = self.current_player()
        if not player:
            raise Exception('No active player')
        player.stand()
        self.next_turn()

    def next_turn(self) -> None:
        self.current_player_index += 1
        if self.current_player_index >= len(self.players):
            self.state = GameState.DEALER_TURN
            self.play_dealer()

    def play_dealer(self) -> None:
        self.dealer.play_turn(self.deck)
        self.state = GameState.FINISHED
        self.resolve_bets()

    def resolve_bets(self) -> None:
        dealer_value = self.dealer.hand.value()
        dealer_bust = self.dealer.hand.is_bust()

        for player in self.players:
            player_value = player.hand.value()
            if player.is_bust:
                player.lose_bet()
            elif dealer_bust or player_value > dealer_value:
                player.win_bet()
            elif player_value == dealer_value:
                player.push_bet()
            else:
                player.lose_bet()

    def get_results(self) -> dict[Player, PlayerBetResult]:
        dealer_value = self.dealer.hand.value()
        dealer_bust = self.dealer.hand.is_bust()
        results: dict[Player, PlayerBetResult] = {}

        for player in self.players:
            player_value = player.hand.value()

            if player.is_bust:
                results[player] = PlayerBetResult.LOSE
            elif dealer_bust or player_value > dealer_value:
                results[player] = PlayerBetResult.WIN
            elif player_value == dealer_value:
                results[player] = PlayerBetResult.PUSH
            else:
                results[player] = PlayerBetResult.LOSE

        return results
