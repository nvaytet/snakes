# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Any

from PIL import Image

from . import config
from .tools import image_to_sprite


class Powerup:
    def __init__(self, x, y, speedup, batch):
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
        self.duration = config.powerup_duration

    def __str__(self):
        return f"Powerup: {self.x} {self.y}"

    def apply(self, player):
        self.avatar.delete()
        player.invincible = True

    def tick(self):
        self.duration -= self.speedup

    def is_expired(self):
        return self.duration <= 0

    def revert(self, player):
        player.invincible = True

    def to_dict(self):
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

    def apply(self, player):
        player.thickness = max(player.thickness - 2, 1)
        super().apply(player)

    def revert(self, player):
        player.thickness += 2
        super().revert(player)


class ThickPowerup(Powerup):
    def __init__(self, *args, **kwargs):
        self.file = config.resources / "thick.png"
        super().__init__(*args, **kwargs)
        self.kind = "thick"

    def apply(self, player):
        player.thickness += 4
        super().apply(player)

    def revert(self, player):
        player.thickness = max(player.thickness - 4, 1)
        super().revert(player)


class GhostPowerup(Powerup):
    def __init__(self, *args, **kwargs):
        self.file = config.resources / "ghost.png"
        super().__init__(*args, **kwargs)
        self.kind = "ghost"

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
