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
        player.picked_up_powerup = True
        pass

    def tick(self):
        self.duration -= 1

    def is_expired(self):
        return self.duration <= 0


class ThinPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "thin.png"
        super().__init__(x, y, batch)

    def apply(self, player):
        player.thickness = max(player.thickness - 2, 1)
        super().apply(player)

    def revert(self, player):
        player.thickness += 2


class ThickPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "thick.png"
        super().__init__(x, y, batch)

    def apply(self, player):
        player.thickness += 2
        super().apply(player)

    def revert(self, player):
        player.thickness = max(player.thickness - 2, 1)


class GhostPowerup(Powerup):
    def __init__(self, x, y, batch):
        self.file = config.resources / "ghost.png"
        super().__init__(x, y, batch)

    def apply(self, player):
        player.ghost = True
        super().apply(player)

    def revert(self, player):
        player.ghost = False
