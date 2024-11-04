# SPDX-License-Identifier: BSD-3-Clause

import importlib_resources as ir
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    fps: int = 30
    resources: Path = ir.files("snakes") / "resources"
    icon_size: int = 32
    head_size: int = 8
    # file = font_manager.findfont("sans")
    # self.large_font = ImageFont.truetype(file, size=16)
    # self.medium_font = ImageFont.truetype(file, size=12)
    # nx: int = 1920  # - self.scoreboard_width
    # ny: int = 1080
    nx: int = 1920  # // 2
    ny: int = 1080  # // 2
    # self.
    # self.time_limit = 60 * 5
    # self.gravity = np.array([0, -1.62])  # m/s^2
    # self.thrust = np.abs(self.gravity[1]) * 3  # m/s^2
    speed: float = 60.0
