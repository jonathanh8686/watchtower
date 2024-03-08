from dataclasses import dataclass
from structs import Action


@dataclass
class PostSmall(Action):
    amount: float


@dataclass
class PostBig(Action):
    amount: float


@dataclass
class Fold(Action):
    pass


@dataclass
class Check(Action):
    pass


@dataclass
class Call(Action):
    amount: float


@dataclass
class Raise(Action):
    amount: float
    all_in: bool = False

@dataclass
class Collected(Action):
    amount: float