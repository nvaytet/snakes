# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass, asdict
import hashlib as hl
from typing import Any

import numpy as np
import pyglet
from matplotlib.colors import to_rgb
from PIL import Image

from . import config
from .tools import Instructions, image_to_sprite


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
        # self.invincible = False
        self.ghost = False
        self.gap = 0
        self.next_gap = np.random.uniform(0, config.gap_period)
        self.speed = config.speed
        self.powerups = []
        # self.color = to_hex(f"C{self.number - 1}")
        self.color = "#" + hl.sha256(self.team.encode()).hexdigest()[:6]
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
        self.update_avatar_thickness()

    def make_avatar(self, batch: pyglet.graphics.Batch):
        raw = Image.open(config.resources / "head.png")
        self.raw_avatar_size = raw.height
        a = np.array(raw)
        b = a[..., :3].sum(axis=2) > 0
        rgb = (np.array(to_rgb(self.color)) * 255).astype("uint8")
        a[b, :3] = rgb
        self.avatar = image_to_sprite(
            Image.fromarray(a),
            x=self.x * config.scaling,
            y=self.y * config.scaling,
            batch=batch,
        )
        self.update_avatar_thickness()
        self.update_avatar_orientation()

    def update_avatar_thickness(self):
        self.avatar.scale = self.thickness * config.scaling / self.raw_avatar_size * 1.8

    def move(self, dt: float):
        vx = self.speed * ((self.direction == "R") - (self.direction == "L"))
        vy = self.speed * ((self.direction == "U") - (self.direction == "D"))
        self.x = (self.x + vx * dt) % config.nx
        self.y = (self.y + vy * dt) % config.ny
        self.avatar.update(x=self.x * config.scaling, y=self.y * config.scaling)

    def position(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    def update_avatar_orientation(self):
        self.avatar.rotation = {"R": 0, "U": 270, "L": 180, "D": 90}[self.direction]

    def turn_left(self):
        directions = "ULDR"
        self.direction = directions[(directions.index(self.direction) + 1) % 4]
        self.update_avatar_orientation()

    def turn_right(self):
        directions = "URDL"
        self.direction = directions[(directions.index(self.direction) + 1) % 4]
        self.update_avatar_orientation()

    def execute_bot_instructions(self, instructions: Instructions | None):
        if instructions is None:
            return
        if instructions.left and instructions.right:
            raise ValueError("Cannot turn left and right at the same time")
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

    def __post_init__(self):
        object.__setattr__(self, "_fields", asdict(self))

    def __getitem__(self, key: str) -> Any:
        return self._fields[key]

    def keys(self):
        return self._fields.keys()

    def values(self):
        return self._fields.values()

    def items(self):
        return self._fields.items()
