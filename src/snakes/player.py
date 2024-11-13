# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional

import numpy as np
from matplotlib.colors import to_hex, to_rgb


from . import config
from .tools import Instructions

import pyglet
from pyglet import shapes


class Player:
    def __init__(
        self,
        number: int,
        team: str,
        position: tuple[float, float],
        score: int = 0,
    ):
        self.team = team
        self.number = number
        self.score = score
        self.finalist = self.score >= config.high_score
        self.winner = self.score >= config.high_score * 10
        self._thickness = config.thickness
        self.invincible = False
        self.ghost = False
        self.gap = 0
        self.next_gap = np.random.uniform(0, config.gap_period)
        self.speed = config.speed
        self.powerups = []
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
        self.direction = np.random.choice(["U", "D", "L", "R"])
        # If player score is crazy high it means they won the match already and
        # shouldn't play
        self.dead = self.score >= config.high_score * 10
        self.x, self.y = position
        print(self.x, self.y)
        # self.landed = False
        self.avatar = None

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        self.avatar.width = value * config.scaling
        self.avatar.height = value * config.scaling
        self.avatar.anchor_position = (
            0.5 * self.avatar.width,
            0.5 * self.avatar.height,
        )

    def make_avatar(self, batch: pyglet.graphics.Batch):
        self.avatar = shapes.Rectangle(
            self.x,
            self.y,
            self._thickness * config.scaling,
            self._thickness * config.scaling,
            color=tuple(int(c * 255) for c in to_rgb(self.color)),
            batch=batch,
        )
        self.avatar.anchor_position = (
            0.5 * self.avatar.width,
            0.5 * self.avatar.height,
        )

    def move(self, dt: float):
        vx = self.speed * ((self.direction == "R") - (self.direction == "L"))
        vy = self.speed * ((self.direction == "U") - (self.direction == "D"))
        self.x += vx * dt
        self.y += vy * dt
        self.avatar.position = (self.x * config.scaling, self.y * config.scaling)

    def position(self):
        return int(self.x), int(self.y)

    def turn_left(self):
        directions = "ULDR"
        self.direction = directions[(directions.index(self.direction) + 1) % 4]

    def turn_right(self):
        directions = "URDL"
        self.direction = directions[(directions.index(self.direction) + 1) % 4]

    def execute_bot_instructions(self, instructions: Optional[Instructions]):
        if instructions is None:
            return
        if instructions.left:
            self.turn_left()
        if instructions.right:
            self.turn_right()
        # self.main_thruster = instructions.main and self.flying
        # self.left_thruster = instructions.left and self.flying
        # self.right_thruster = instructions.right and self.flying

    def die(self):
        self.dead = True
        print(f"Player {self.team} died")

    # def update_scoreboard(self, batch: pyglet.graphics.Batch):
    #     img = Image.new("RGBA", (150, 54), (0, 0, 0, 0))
    #     texts = [
    #         f"Team {self.team}",
    #         f"x={self.x:.1f}, y={self.y:.1f}",
    #         f"v=[{self.velocity[0]:.1f}, {self.velocity[1]:.1f}]",
    #         f"θ={self.heading:.1f}, fuel={self.fuel:.1f}",
    #     ]
    #     for i, text in enumerate(texts):
    #         img.paste(
    #             text_to_raw_image(
    #                 text,
    #                 width=150,
    #                 height=24,
    #                 font=config.medium_font,
    #             ),
    #             (0, 14 * i),
    #         )

    #     if self.score_text is not None:
    #         self.score_text.delete()
    #     self.score_text = image_to_sprite(
    #         img=img,
    #         x=config.nx + 55,
    #         y=config.ny - 120 - 75 * self.number,
    #         batch=batch,
    #         recenter=False,
    #     )

    def to_dict(self) -> dict:
        return {
            "team": self.team,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "speed": config.speed,
            "dead": self.dead,
        }
