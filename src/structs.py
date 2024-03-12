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

    def __hash__(self) -> int:
        return hash(self.uid)


@dataclass
class Action:
    player: Player


class Ply:
    def __init__(self):
        self.id: str | None = ""
        self.players: list[Player] = []
        self.board: list[Card | None] = []
        self.stacks: dict[Player, float] = {}
        self.state: PlyState = PlyState.PREFLOP
        self.cards: dict[Player, tuple[Card, Card]] = {}
        self.positions: dict[Player, int] = {}
        self.dealer: Player | None = None
        self.actions: dict[PlyState, list[tuple[Player, Action]]] = {}
    
    def set_positions(self, positions: dict[Player, int]) -> None:
        self.positions = positions.copy()
    
    def process_start(self, ply_id: str, dealer: Player | None) -> None:
        self.id = ply_id
        self.dealer = dealer

    def process_stacks(self, stacks: dict[Player, float]):
        self.stacks = stacks.copy()

    def process_flop(self, flop: list[Card]) -> None:
        if self.state != PlyState.PREFLOP:
            raise ValueError("Flop can only be processed at preflop")
        self.board.extend(flop.copy())
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

    def add_card_data(self, player: Player, cards: tuple[Card, Card]) -> None:
        self.cards[player] = cards
    