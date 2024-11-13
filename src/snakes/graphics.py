# SPDX-License-Identifier: BSD-3-Clause

from matplotlib import colors as mcolors
import numpy as np
import pyglet
from PIL import Image

from . import config
from .tools import image_to_imagedata, image_to_sprite


class Graphics:
    def __init__(self, fullscreen: bool = False, players: dict = None):
        self.window = pyglet.window.Window(
            config.window_size[0],
            config.window_size[1],
            fullscreen=fullscreen,
            resizable=not fullscreen,
        )

        self.background_batch = pyglet.graphics.Batch()
        self.main_batch = pyglet.graphics.Batch()

        self.cmap = mcolors.ListedColormap(
            ["black"] + [p.color for p in players.values()] + ["grey"]
        )

        img = Image.fromarray(
            np.flipud(np.zeros((config.ny, config.nx, 4), dtype=np.uint8))
        )
        self.background = image_to_sprite(
            img,
            x=0,
            y=0,
            batch=self.background_batch,
            anchor=(0, 0),
            recenter=False,
        )
        self.background.scale = config.scaling
        self.exit_message = None

        @self.window.event
        def on_draw():
            self.window.clear()
            self.background_batch.draw()
            self.main_batch.draw()

    def update_scores(self, players: dict):
        self.window.set_caption(
            "          ".join(
                [
                    f"{p.team}={'FINALIST' if p.finalist else p.score}"
                    for p in players.values()
                    if not p.winner
                ]
            )
        )

    def update(self, array: np.ndarray):
        img = Image.fromarray(np.flipud((self.cmap(array) * 255).astype("uint8")))
        self.background.image = image_to_imagedata(img, anchor=(0, 0), recenter=False)

    def show_exit_message(self, message):
        self.exit_message = pyglet.text.Label(
            message,
            color=(255, 255, 255, 255),
            font_size=80,
            x=config.window_size[0] * 0.5,
            y=config.window_size[1] * 0.5,
            batch=self.main_batch,
            anchor_x="center",
            anchor_y="center",
        )
