from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


WHITE = 0
BLACK = 1
BAR = -1


type Player = Literal[0] | Literal[1]
type OptionalPlayer = Player | None


@dataclass
class Dice:

    die1: int  # 1..6
    die2: int  # 1..6

    def copy(self) -> Dice:
        return Dice(self.die1, self.die2)

    def is_double(self) -> bool:
        return self.die1 == self.die2

    def is_valid(self) -> bool:

        return 1 <= self.die1 <= 6 and 1 <= self.die2 <= 6


class DiceCup:

    _a = 1664525
    _c = 1013904223
    _m = 2**32
    _seed: int

    def __init__(self, seed: int):
        self._seed = seed

    def roll(self) -> Dice:
        return Dice((self._next() % 1009) % 6 + 1, (self._next() % 1009) % 6 + 1)

    def _next(self) -> int:
        self._seed = (self._a * self._seed + self._c) % self._m
        return self._seed


@dataclass
class Jump:

    point: int  # 0..23 | -1 (bar)
    pips: int  # 1..6


@dataclass
class Move:

    jumps: list[Jump]  # length 0-4


class Board:

    def __init__(self, dice: Dice, turn: int = 1, cells: list[int] | None = None, barW: int = 0, barB: int = 0) -> None:
        """..."""
        ...

    def copy(self) -> Board:
        """..."""
        ...

    def flip(self) -> Board:
        """..."""
        ...

    def cells(self) -> list[int]:
        """..."""
        ...

    def cell(self, i: int) -> int:
        """..."""
        ...

    def bar(self, player: Player) -> int:
        """..."""
        ...

    def off(self, player: Player) -> int:
        """..."""
        ...

    def dice(self) -> Dice:
        """..."""
        ...

    def turn(self) -> int:
        """..."""
        ...

    def current(self) -> OptionalPlayer:
        """..."""
        ...

    def winner(self) -> OptionalPlayer:
        """..."""
        ...

    def over(self) -> bool:
        """..."""
        ...

    def valid_moves(self) -> list[Move]:
        """..."""
        ...

    def is_valid_move(self, move: Move) -> bool:
        """..."""
        ...

    def play(self, move: Move) -> Board:
        """..."""
        ...

    def next(self, dice: Dice) -> Board:
        """..."""
        ...
