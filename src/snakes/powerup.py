from PIL import Image

from . import config
from .tools import image_to_sprite


class Powerup:
    def __init__(self, x, y, batch):
        self.x = x
        self.y = y
        print("making avatar")
        self.avatar = image_to_sprite(Image.open(self.file), x=x, y=y, batch=batch)
        print(self.avatar)
        print(self)

    def __str__(self):
        return f"Powerup: {self.x} {self.y}"

    def apply(self, player):
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
        player.thickness = 1
