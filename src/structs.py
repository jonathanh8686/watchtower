from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class CardSuit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"

class PlyState(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3


@dataclass
class PokerEvent:
    entry: str
    timestamp: datetime
    order: int


@dataclass
class Card:
    rank: int
    suit: CardSuit


@dataclass
class Player:
    username: str
    uid: str


@dataclass
class Action:
    player: Player


class Ply:
    def __init__(self):
        self.board: list[Card | None] = []
        self.players: list[Player] = []
        self.state: PlyState = PlyState.PREFLOP
        self.actions: dict[PlyState, list[tuple[Player, Action]]] = {}

    def process_flop(self, flop: list[Card]) -> None:
        if self.state != PlyState.PREFLOP:
            raise ValueError("Flop can only be processed at preflop")
        self.board.extend(flop)
        self.state = PlyState.FLOP

    def process_turn(self, turn: Card) -> None:
        if self.state != PlyState.FLOP:
            raise ValueError("Flop can only be processed at flop")
        self.board.append(turn)
        self.state = PlyState.TURN

    def process_river(self, river: Card) -> None:
        if self.state != PlyState.TURN:
            raise ValueError("Flop can only be processed at turn")
        self.board.append(river)
        self.state = PlyState.RIVER

    def add_action(self, player: Player, action: Action) -> None:
        if self.state not in self.actions:
            self.actions[self.state] = []
        self.actions[self.state].append((player, action))

    def add_player(self, player: Player) -> None:
        self.players.append(player)
