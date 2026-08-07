# SPDX-License-Identifier: BSD-3-Clause

import importlib
import sys
from pathlib import Path

import snakes


root = Path(__file__).resolve().parent
bots_dir = root / "bots"

sys.path.insert(0, str(bots_dir))

bots = []

for path in bots_dir.iterdir():
    if not path.is_dir():
        continue
    if not path.name.endswith("_bot"):
        continue
    if not (path / "__init__.py").exists():
        continue

    module = importlib.import_module(path.name)
    bots.append(module.Bot())


snakes.play(
    bots=bots,  # List of bots to use
    manual=False,  # Set to True to play manually using the keyboard arrow keys
    speedup=1,  # Increase to speed up the game (no guarantees this works very well)
    test=False,  # Set to True to run in test mode
)
