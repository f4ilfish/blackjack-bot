import random
from enum import Enum

from bot.game.models.constants import INIT_TURN_CARD_COUNT, MAX_PLAYERS
from bot.game.models.deck import Deck
from bot.game.models.player import Dealer, Player, PlayerBetResult, PlayerState


class GameState(Enum):
    WAITING_FOR_PLAYERS = 'waiting'
    WAITING_FOR_BETS = 'waiting_for_bets'
    PLAYER_TURN = 'player_turn'
    DEALER_TURN = 'dealer_turn'
    FINISHED = 'finished'


class GameSession:
    def __init__(
        self,
        game_id: int,
        deck: Deck | None = None,
        players: list[Player] | None = None,
        dealer: Dealer | None = None,
        state: GameState = GameState.WAITING_FOR_PLAYERS,
        current_player: Player | None = None,
    ):
        self.game_id = game_id
        self.deck = Deck() if deck is None else deck
        self.players = [] if players is None else players
        self.dealer = Dealer() if dealer is None else dealer
        self.state = state
        self.current_player = current_player

    def add_player(self, player: Player) -> None:
        if self.state != GameState.WAITING_FOR_PLAYERS:
            raise Exception('Cannot join after game has started')
        if len(self.players) == MAX_PLAYERS:
            raise Exception('Too many players')
        self.players.append(player)

    def start_betting_phase(self) -> None:
        if not self.players:
            raise Exception('No players in game')
        for player in self.players:
            player.state = PlayerState.BET
        self.state = GameState.WAITING_FOR_BETS

    def is_all_bets_placed(self) -> bool:
        return all(player.bet > 0 for player in self.players)

    def start_game(self) -> None:
        if self.state != GameState.WAITING_FOR_BETS:
            raise Exception('Must be in betting phase to start game')
        if not self.is_all_bets_placed():
            raise Exception('All players must place bets')

        # При первой раздаче карт на 7 игроков точно хватит
        for _ in range(INIT_TURN_CARD_COUNT):
            for player in self.players:
                player.hit(self.deck.draw())  # type: ignore
            self.dealer.hit(self.deck.draw()) # type: ignore

        for player in self.players:
            player.state = PlayerState.WAIT_TURN

        # Дополнительный элемент случайности
        random.shuffle(self.players)
        self.current_player = self.players[0]
        self.current_player.state = PlayerState.TURN
        self.state = GameState.PLAYER_TURN

    def next_turn(self) -> None:
        if self.state != GameState.PLAYER_TURN:
            return None
        if (
            self.current_player is None
            or self.current_player.state != PlayerState.END_TURN
        ):
            return None
        for player in self.players:
            if player.state == PlayerState.WAIT_TURN:
                self.current_player = player
                self.current_player.state = PlayerState.TURN
                return None
        self.state = GameState.DEALER_TURN
        self.play_dealer()
        return None

    def player_action_hit(self, user_id: int) -> None:
        if self.state != GameState.PLAYER_TURN:
            return None
        if self.current_player is None or self.current_player.user_id != user_id:
            return None
        card = self.deck.draw()
        # Проанализировать потенциальную возможность при 7 игроках
        if card is None:
            for player in self.players:
                player.state = PlayerState.END_TURN
            self.dealer.state = PlayerState.END_TURN
            self.state = GameState.FINISHED
            return None
        self.current_player.hit(card)
        if self.current_player.is_bust():
            self.current_player.state = PlayerState.END_TURN
            self.next_turn()
            return None
        return None

    def player_action_stand(self, user_id: int) -> None:
        if self.state != GameState.PLAYER_TURN:
            return None
        if self.current_player is None or self.current_player.user_id != user_id:
            return None
        self.current_player.stand()
        self.next_turn()
        return None

    def play_dealer(self) -> None:
        if self.state != GameState.DEALER_TURN:
            return None
        self.dealer.play_turn(self.deck)
        self.state = GameState.FINISHED
        self.resolve_bets()
        return None

    def resolve_bets(self) -> None:
        dealer_value = self.dealer.hand.value()
        dealer_bust = self.dealer.hand.is_bust()

        for player in self.players:
            player_value = player.hand.value()
            if player.is_bust():
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

            if player.is_bust():
                results[player] = PlayerBetResult.LOSE
            elif dealer_bust or player_value > dealer_value:
                results[player] = PlayerBetResult.WIN
            elif player_value == dealer_value:
                results[player] = PlayerBetResult.PUSH
            else:
                results[player] = PlayerBetResult.LOSE

        return results
