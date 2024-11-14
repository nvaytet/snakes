# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Any

import pyglet
from PIL import Image


@dataclass
class Instructions:
    """
    Instructions for the snake.
    """

    left: bool = False
    right: bool = False


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


def recenter_image(img: pyglet.image.ImageData) -> pyglet.image.ImageData:
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img


def image_to_imagedata(img, anchor=None, recenter=True):
    imd = pyglet.image.ImageData(
        width=img.width,
        height=img.height,
        fmt="RGBA",
        data=img.tobytes(),
        pitch=-img.width * 4,
    )
    if anchor is not None:
        imd.anchor_x = anchor[0]
        imd.anchor_y = anchor[1]
    elif recenter:
        imd = recenter_image(imd)
    return imd


def image_to_sprite(
    img: Image,
    x: float,
    y: float,
    batch: pyglet.graphics.Batch,
    recenter: bool = True,
    anchor: tuple[float, float] | None = None,
) -> pyglet.sprite.Sprite:
    imd = image_to_imagedata(img, anchor=anchor, recenter=recenter)
    return pyglet.sprite.Sprite(img=imd, x=x, y=y, batch=batch)
