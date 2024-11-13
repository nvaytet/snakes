# SPDX-License-Identifier: BSD-3-Clause

from matplotlib import colors as mcolors
import numpy as np
import pyglet
from PIL import Image

from . import config
from .tools import image_to_imagedata, image_to_sprite

# from .terrain import Terrain


# def recenter_image(img: pyglet.image.ImageData) -> pyglet.image.ImageData:
#     img.anchor_x = img.width // 2
#     img.anchor_y = img.height // 2
#     return img


# def image_to_imagedata(img, anchor=None, recenter=True):
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
#     return imd


# def image_to_sprite(
#     img: Image,
#     x: float,
#     y: float,
#     batch: pyglet.graphics.Batch,
#     recenter: bool = True,
#     anchor: tuple[float, float] | None = None,
# ) -> pyglet.sprite.Sprite:
#     imd = image_to_imagedata(img, anchor=anchor, recenter=recenter)
#     return pyglet.sprite.Sprite(img=imd, x=x, y=y, batch=batch)


class Graphics:
    def __init__(self, fullscreen: bool = False, players: dict = None):
        self.window = pyglet.window.Window(
            config.window_size[0],
            config.window_size[1],
            # caption=", ".join(f"{p.team}: {p.score}" for p in players.values()),
            fullscreen=fullscreen,
            resizable=not fullscreen,
        )
        # self.up

        self.background_batch = pyglet.graphics.Batch()
        self.main_batch = pyglet.graphics.Batch()

        # self.cmap = mcolors.ListedColormap(
        #     ["grey"] + [p.color for p in players.values()] + ["magenta"]
        # )
        self.cmap = mcolors.ListedColormap(
            ["black"] + [p.color for p in players.values()] + ["grey"]
        )

        # self.background = np.zeros((config.ny, config.nx, 3), dtype=np.uint8)
        img = Image.fromarray(
            np.flipud(np.zeros((config.ny, config.nx, 4), dtype=np.uint8))
        )
        self.background = image_to_sprite(
            # img, x=1000, y=500, batch=self.main_batch, recenter=False
            img,
            x=0,
            y=0,
            batch=self.background_batch,
            anchor=(0, 0),
            recenter=False,
        )
        self.background.scale = config.scaling
        # self.background.z = -10

        # self.star_batch = pyglet.graphics.Batch()
        # self.background_batch = pyglet.graphics.Batch()
        # self.update(array=np.zeros((config.ny // 2, config.nx // 2), dtype=np.uint8))
        # self.time_label = pyglet.sprite.Sprite(
        #     img=text_to_image(
        #         "Time left:", width=100, height=24, font=config.large_font
        #     ),
        #     x=config.nx + 20,
        #     y=config.ny - 30,
        #     batch=self.main_batch,
        # )
        # self.time_left = None
        self.exit_message = None
        # self.make_stars()

        @self.window.event
        def on_draw():
            self.window.clear()
            # self.background.get_texture().blit(0, 0)
            # self.star_batch.draw()
            self.background_batch.draw()
            self.main_batch.draw()

    def update_scores(self, players: dict):
        # texts = []
        # for p in players.values():
        #     if not p.winner:
        #         texts.append(f"{p.team}: {"FINALIST" if p.finalist else p.score}")
        self.window.set_caption(
            "          ".join(
                [
                    f"{p.team}={'FINALIST' if p.finalist else p.score}"
                    for p in players.values()
                    if not p.winner
                ]
            )
        )

    def update(self, array: np.ndarray, players: list = None):
        # self.background = array
        img = Image.fromarray(np.flipud((self.cmap(array) * 255).astype("uint8")))
        # img = Image.fromarray((self.cmap(array) * 255).astype("uint8"))
        # self.background.data = img.tobytes()
        self.background.image = image_to_imagedata(img, anchor=(0, 0), recenter=False)
        # self.background = pyglet.image.ImageData(
        #     width=img.width,
        #     height=img.height,
        #     fmt="RGBA",
        #     data=img.tobytes(),
        #     pitch=-img.width * 4,
        # )

    # def make_stars(self):
    #     self.stars = []
    #     self.star_t0 = np.random.uniform(0, config.twinkle_period, config.nstars)
    #     xstar = np.random.uniform(0, config.nx, config.nstars)
    #     ystar = np.random.uniform(0, config.ny, config.nstars)
    #     for x, y in zip(xstar, ystar):
    #         self.stars.append(
    #             pyglet.shapes.Circle(
    #                 x, y, 1, color=(255, 255, 255, 255), batch=self.star_batch
    #             )
    #         )

    # def update_stars(self, t: float):
    #     for star, t0 in zip(self.stars, self.star_t0):
    #         star.opacity = int(
    #             255
    #             * np.sin(
    #                 np.pi * ((t % config.twinkle_period) - t0) / config.twinkle_period
    #             )
    #             ** 2
    #         )

    # def update_scoreboard(self, t: float):
    #     if self.time_left is not None:
    #         self.time_left.delete()
    #     t_str = str(datetime.timedelta(seconds=int(t)))[2:]
    #     self.time_left = pyglet.sprite.Sprite(
    #         img=text_to_image(t_str, width=100, height=24, font=config.large_font),
    #         x=self.time_label.x + 90,
    #         y=self.time_label.y,
    #         batch=self.main_batch,
    #     )

    def show_exit_message(self, message):
        self.exit_message = pyglet.text.Label(
            message,
            # color=(153, 51, 153, 255),
            color=(255, 255, 255, 255),
            font_size=80,
            x=config.window_size[0] * 0.5,
            y=config.window_size[1] * 0.5,
            batch=self.main_batch,
            anchor_x="center",
            anchor_y="center",
        )

    # def show_end_of_match_message(self, winner):
    #     self.exit_message = pyglet.text.Label(
    #         f"{winner} wins the match!",
    #         color=(255, 255, 255, 255),
    #         font_size=80,
    #         x=config.window_size[0] * 0.5,
    #         y=config.window_size[1] * 0.5,
    #         batch=self.main_batch,
    #         anchor_x="center",
    #         anchor_y="center",
    #     )
