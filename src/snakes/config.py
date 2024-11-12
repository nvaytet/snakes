# SPDX-License-Identifier: BSD-3-Clause

import importlib_resources as ir
from pathlib import Path


# @dataclass(frozen=True)
class Config:
    def __init__(self):
        self.fps: int = 30
        self.resources: Path = ir.files("snakes") / "resources"
        # self.icon_size: int = 32
        # self.head_size: int = 8
        # file = font_manager.findfont("sans")
        # self.large_font = ImageFont.truetype(file, size=16)
        # self.medium_font = ImageFont.truetype(file, size=12)
        # nx: int = 1920  # - self.scoreboard_width
        # ny: int = 1080
        self.scaling = 2
        self.window_size = (1920, 1080)
        self.nx: int = self.window_size[0] // self.scaling
        self.ny: int = self.window_size[1] // self.scaling
        self.thickness = 3
        self.powerup_size = 32
        self.powerup_duration = 8 * self.fps
        self.gap_period = 8.0
        self.gap_duration = 0.25
        self.max_powerups = 2
        self.no_powerups = 10
        # self.time_limit = 60 * 5
        # self.gravity = np.array([0, -1.62])  # m/s^2
        # self.thrust = np.abs(self.gravity[1]) * 3  # m/s^2
        self.speed: float = 60  # 60.0
