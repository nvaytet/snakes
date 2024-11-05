# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional

import numpy as np
import pyglet
from matplotlib.colors import to_hex
from PIL import Image

from . import config
from .tools import Instructions, image_to_sprite, text_to_raw_image


class Player:
    def __init__(
        self,
        number: int,
        team: str,
        # color: str,
        position: tuple[float, float],
        # avatar: Union[int, str],
        # position: float,
        # back_batch: pyglet.graphics.Batch,
        # main_batch: pyglet.graphics.Batch,
    ):
        self.team = team
        self.number = number
        self.score = 0
        self.thickness = config.thickness
        # self.score_text = None
        # self._main_thruster = False
        # self._left_thruster = False
        # self._right_thruster = False
        # self.fuel = config.max_fuel
        # self.velocity = np.array([40.0, 0.0])

        # self._rotate_left = False
        # self._rotate_right = False
        self.color = to_hex(f"C{self.number-1}")
        # self.make_avatar(
        #     avatar=avatar,
        #     position=position,
        #     back_batch=back_batch,
        #     main_batch=main_batch,
        # )
        self.direction = "U"
        self.dead = False
        self.x, self.y = position
        print(self.x, self.y)
        # self.landed = False

    def move(self, dt: float):
        vx = config.speed * ((self.direction == "R") - (self.direction == "L"))
        vy = config.speed * ((self.direction == "U") - (self.direction == "D"))
        self.x += vx * dt
        self.y += vy * dt

    def position(self):
        return int(self.x), int(self.y)

    def turn_left(self):
        directions = "ULDR"
        self.direction = directions[(directions.index(self.direction) + 1) % 4]

    def turn_right(self):
        directions = "URDL"
        self.direction = directions[(directions.index(self.direction) + 1) % 4]

    def crash(self, reason: str):
        self.dead = True
        # x, y = self.x, self.y
        img = Image.open(config.resources / "skull.png")
        img = img.resize(config.avatar_size).convert("RGBA")
        data = img.getdata()
        array = np.array(data).reshape(img.height, img.width, 4)
        rgb = hex2color(self.color)
        for i in range(3):
            array[..., i] = int(round(rgb[i] * 255))

        av_image = Image.fromarray(array.astype(np.uint8))
        batch = self.avatar.batch
        self.avatar.delete()
        self.avatar = image_to_sprite(
            img=av_image,
            x=self.x,
            y=self.y,
            batch=batch,
        )
        self.score_avatar.delete()
        self.score_avatar = image_to_sprite(
            img=av_image,
            x=config.nx + 30,
            y=config.ny - 100 - 75 * self.number,
            batch=batch,
        )
        print(f"Player {self.team} crashed! Reason: {reason}.")

    def land(
        self, time_left: float, landing_site_width: int, flag: Optional[str] = None
    ):
        self.landed = True
        score_breakdown = {
            "landing": config.score_landing_bonus,
            "site width": config.score_landing_site_bonus
            * (config.avatar_size[0] / landing_site_width),
            "time": config.score_time_bonus * (time_left / config.time_limit),
            "fuel": config.score_fuel_bonus * (self.fuel / config.max_fuel),
        }
        self.score = int(round(sum(score_breakdown.values())))
        print(
            f"Player {self.team} landed! Score={self.score}: "
            + ", ".join([f"{k}={v:.1f}" for k, v in score_breakdown.items()])
        )
        if flag is not None:
            try:
                img = Image.open(config.resources / "flags" / f"{flag}.png")
            except FileNotFoundError:
                img = Image.open(flag)
            width = int(config.avatar_size[0] / 1.5)
            height = int(width * (img.height / img.width))
            img = img.resize((width, height)).convert("RGBA")
            dx = config.avatar_size[0] // 5

            batch = self.avatar.batch
            self.flag = image_to_sprite(
                img=img,
                x=self.avatar.x + dx,
                y=self.avatar.y + dx,
                batch=batch,
                recenter=False,
            )
            self.score_flag = image_to_sprite(
                img=img,
                x=self.score_avatar.x + dx,
                y=self.score_avatar.y + dx,
                batch=batch,
                recenter=False,
            )

    def execute_bot_instructions(self, instructions: Optional[Instructions]):
        if instructions is None:
            return
        self.main_thruster = instructions.main and self.flying
        self.left_thruster = instructions.left and self.flying
        self.right_thruster = instructions.right and self.flying

    def update_scoreboard(self, batch: pyglet.graphics.Batch):
        img = Image.new("RGBA", (150, 54), (0, 0, 0, 0))
        texts = [
            f"Team {self.team}",
            f"x={self.x:.1f}, y={self.y:.1f}",
            f"v=[{self.velocity[0]:.1f}, {self.velocity[1]:.1f}]",
            f"θ={self.heading:.1f}, fuel={self.fuel:.1f}",
        ]
        for i, text in enumerate(texts):
            img.paste(
                text_to_raw_image(
                    text,
                    width=150,
                    height=24,
                    font=config.medium_font,
                ),
                (0, 14 * i),
            )

        if self.score_text is not None:
            self.score_text.delete()
        self.score_text = image_to_sprite(
            img=img,
            x=config.nx + 55,
            y=config.ny - 120 - 75 * self.number,
            batch=batch,
            recenter=False,
        )

    def to_dict(self) -> dict:
        return {
            "team": self.team,
            "position": (self.position[0], self.position[1]),
            "velocity": (self.velocity[0], self.velocity[1]),
            "heading": self.heading,
            "fuel": self.fuel,
            "dead": self.dead,
            "landed": self.landed,
        }
