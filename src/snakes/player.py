# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional

from matplotlib.colors import to_hex

from . import config
from .tools import Instructions


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
