# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Any

import pyglet
from PIL import Image

from . import config
from .player import Player
from .tools import image_to_sprite


def _change_thickness(value: int, direction: str) -> int:
    thicknesses = [1, 3, 7, 15, 31, 63, 127, 255]
    index = thicknesses.index(value)
    if direction == "up":
        index = min(index + 1, len(thicknesses) - 1)
    elif direction == "down":
        index = max(index - 1, 0)
    return thicknesses[index]


class Powerup:
    def __init__(self, x: float, y: float, speedup: int, batch: pyglet.graphics.Batch):
        self.x = x
        self.y = y
        self.kind = None
        self.speedup = speedup
        self.avatar = image_to_sprite(
            Image.open(self.file),
            x=x * config.scaling,
            y=y * config.scaling,
            batch=batch,
        )
        self.lifetime = config.powerup_lifetime * config.fps

    def __str__(self) -> str:
        return f"Powerup: {self.x} {self.y}"

    def age(self):
        self.lifetime -= self.speedup

    def apply(self, player: Player):
        self.avatar.delete()
        # player.invincible = True

    def tick(self):
        self.duration -= self.speedup

    def is_expired(self) -> bool:
        return self.duration <= 0

    def revert(self, player):
        # player.invincible = True
        return

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "x": self.x,
            "y": self.y,
        }


@dataclass(frozen=True)
class PowerupInfo:
    """
    Information about a powerup.
    """

    x: float
    y: float
    kind: str

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class ThinPowerup(Powerup):
    def __init__(self, *args, **kwargs):
        self.file = config.resources / "thin.png"
        super().__init__(*args, **kwargs)
        self.kind = "thin"
        self.duration = 10 * config.fps

    def apply(self, player):
        player.thickness = _change_thickness(player.thickness, "down")
        super().apply(player)

    def revert(self, player):
        player.thickness = _change_thickness(player.thickness, "up")
        super().revert(player)


class ThickPowerup(Powerup):
    def __init__(self, *args, **kwargs):
        self.file = config.resources / "thick.png"
        super().__init__(*args, **kwargs)
        self.kind = "thick"
        self.duration = 10 * config.fps

    def apply(self, player):
        player.thickness = _change_thickness(player.thickness, "up")
        super().apply(player)

    def revert(self, player):
        player.thickness = _change_thickness(player.thickness, "down")
        super().revert(player)


class GhostPowerup(Powerup):
    def __init__(self, *args, **kwargs):
        self.file = config.resources / "ghost.png"
        super().__init__(*args, **kwargs)
        self.kind = "ghost"
        self.duration = 8 * config.fps

    def apply(self, player):
        player.ghost = True
        super().apply(player)

    def revert(self, player):
        player.ghost = False
        super().revert(player)


class ClearPowerup(Powerup):
    def __init__(self, *args, **kwargs):
        self.file = config.resources / "clear.png"
        super().__init__(*args, **kwargs)
        self.kind = "clear"


class FastPowerup(Powerup):
    def __init__(self, *args, **kwargs):
        self.file = config.resources / "fast.png"
        super().__init__(*args, **kwargs)
        self.kind = "fast"
        self.duration = 10 * config.fps

    def apply(self, player):
        player.speed += 30
        super().apply(player)

    def revert(self, player):
        player.speed = max(player.speed - 30, 1)
        super().revert(player)


class SlowPowerup(Powerup):
    def __init__(self, *args, **kwargs):
        self.file = config.resources / "slow.png"
        super().__init__(*args, **kwargs)
        self.kind = "slow"
        self.duration = 10 * config.fps

    def apply(self, player):
        player.speed -= 30
        super().apply(player)

    def revert(self, player):
        player.speed = max(player.speed + 30, 1)
        super().revert(player)


listing = {
    ThinPowerup: 1,
    ThickPowerup: 1,
    GhostPowerup: 1,
    ClearPowerup: 0.3,
    FastPowerup: 1,
    SlowPowerup: 1,
}

psum = sum(listing.values())
all_powerups = {k: v / psum for k, v in listing.items()}
