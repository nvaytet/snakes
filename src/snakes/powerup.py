from PIL import Image

from . import config
from .tools import image_to_sprite


class Powerup:
    def __init__(self, x, y, batch):
        self.x = x
        self.y = y
        print("making avatar", x, y)
        self.avatar = image_to_sprite(
            Image.open(self.file),
            x=x * config.scaling,
            y=y * config.scaling,
            batch=batch,
        )
        self.duration = config.powerup_duration
        print(self.avatar)
        print(self)

    def __str__(self):
        return f"Powerup: {self.x} {self.y}"

    def apply(self, player):
        self.avatar.delete()
        player.invincible = True

    def tick(self):
        self.duration -= 1

    def is_expired(self):
        return self.duration <= 0

    def revert(self, player):
        player.invincible = True


class ThinPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "thin.png"
        super().__init__(x, y, batch)

    def apply(self, player):
        player.thickness = max(player.thickness - 2, 1)
        super().apply(player)

    def revert(self, player):
        player.thickness += 2
        super().revert(player)


class ThickPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "thick.png"
        super().__init__(x, y, batch)

    def apply(self, player):
        player.thickness += 4
        super().apply(player)

    def revert(self, player):
        player.thickness = max(player.thickness - 4, 1)
        super().revert(player)


class GhostPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "ghost.png"
        super().__init__(x, y, batch)

    def apply(self, player):
        player.ghost = True
        super().apply(player)

    def revert(self, player):
        player.ghost = False
        super().revert(player)


class ClearPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "clear.png"
        super().__init__(x, y, batch)


class FastPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "fast.png"
        super().__init__(x, y, batch)

    def apply(self, player):
        player.speed += 30
        super().apply(player)

    def revert(self, player):
        player.speed = max(player.speed - 30, 1)
        super().revert(player)


class SlowPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "slow.png"
        super().__init__(x, y, batch)

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
