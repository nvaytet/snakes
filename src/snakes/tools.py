# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Any, Optional

import pyglet
from PIL import Image, ImageDraw, ImageFont

from . import config


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

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


def text_to_raw_image(
    text: str, width: float, height: float, font: Optional[ImageFont.ImageFont] = None
) -> Image:
    if font is None:
        font = config.large_font
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text(
        (0, 0),
        text,
        fill=(255, 255, 255),
        font=font,
    )
    return img


def text_to_image(
    text: str, width: float, height: float, font: Optional[ImageFont.ImageFont] = None
) -> pyglet.image.ImageData:
    img = text_to_raw_image(text, width, height, font=font)
    return pyglet.image.ImageData(
        width=img.width,
        height=img.height,
        fmt="RGBA",
        data=img.tobytes(),
        pitch=-img.width * 4,
    )


# def recenter_image(img: pyglet.image.ImageData) -> pyglet.image.ImageData:
#     img.anchor_x = img.width // 2
#     img.anchor_y = img.height // 2
#     return img


# def image_to_sprite(
#     img: Image,
#     x: float,
#     y: float,
#     batch: pyglet.graphics.Batch,
#     recenter: bool = True,
#     anchor: Optional[Tuple[float, float]] = None,
# ) -> pyglet.sprite.Sprite:
#     imd = pyglet.image.ImageData(
#         width=img.width,
#         height=img.height,
#         fmt="RGBA",
#         data=img.tobytes(),
#         pitch=-img.width * 4,
#     )
#     if anchor is not None:
#         imd.anchor_x = anchor[0]
#         imd.anchor_y = anchor[1]
#     elif recenter:
#         imd = recenter_image(imd)
#     return pyglet.sprite.Sprite(img=imd, x=x, y=y, batch=batch)


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
