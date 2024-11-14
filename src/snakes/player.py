# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
from matplotlib.colors import to_hex, to_rgb


from . import config
from .tools import Instructions

import pyglet
from pyglet import shapes


class Player:
    def __init__(
        self,
        number: int,
        team: str,
        position: tuple[float, float],
        score: int = 0,
    ):
        self.team = team
        self.number = number
        self.score = score
        self.finalist = self.score >= config.high_score
        self.winner = self.score >= config.high_score * 10
        self._thickness = config.thickness
        self.invincible = False
        self.ghost = False
        self.gap = 0
        self.next_gap = np.random.uniform(0, config.gap_period)
        self.speed = config.speed
        self.powerups = []
        self.color = to_hex(f"C{self.number-1}")
        self.direction = np.random.choice(["U", "D", "L", "R"])
        # If player score is crazy high it means they won the match already and
        # shouldn't play
        self.dead = self.score >= config.high_score * 10
        self.x, self.y = position
        self.avatar = None

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        self.avatar.width = value * config.scaling
        self.avatar.height = value * config.scaling
        self.avatar.anchor_position = (
            0.5 * self.avatar.width,
            0.5 * self.avatar.height,
        )

    def make_avatar(self, batch: pyglet.graphics.Batch):
        self.avatar = shapes.Rectangle(
            self.x,
            self.y,
            self._thickness * config.scaling,
            self._thickness * config.scaling,
            color=tuple(int(c * 255) for c in to_rgb(self.color)),
            batch=batch,
        )
        self.avatar.anchor_position = (
            0.5 * self.avatar.width,
            0.5 * self.avatar.height,
        )

    def move(self, dt: float):
        vx = self.speed * ((self.direction == "R") - (self.direction == "L"))
        vy = self.speed * ((self.direction == "U") - (self.direction == "D"))
        self.x += vx * dt
        self.y += vy * dt
        self.avatar.position = (self.x * config.scaling, self.y * config.scaling)

    def position(self):
        return int(self.x), int(self.y)

    def turn_left(self):
        directions = "ULDR"
        self.direction = directions[(directions.index(self.direction) + 1) % 4]

    def turn_right(self):
        directions = "URDL"
        self.direction = directions[(directions.index(self.direction) + 1) % 4]

    def execute_bot_instructions(self, instructions: Optional[Instructions]):
        if instructions is None:
            return
        if instructions.left:
            self.turn_left()
        if instructions.right:
            self.turn_right()

    def die(self):
        self.dead = True
        print(f"Player {self.team} died")

    def to_dict(self) -> dict:
        return {
            "team": self.team,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "speed": config.speed,
            "dead": self.dead,
            "score": self.score,
            "thickness": self.thickness,
            "number": self.number,
            "ghost": any(powerup.kind == "ghost" for powerup in self.powerups),
            "finalist": self.finalist,
        }


@dataclass(frozen=True)
class PlayerInfo:
    """
    Information about a player.
    """

    team: str
    x: float
    y: float
    direction: str
    speed: float
    dead: bool
    score: int
    thickness: int
    number: int
    ghost: bool
    finalist: bool

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
