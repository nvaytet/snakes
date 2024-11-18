# SPDX-License-Identifier: BSD-3-Clause

import glob
import importlib

import snakes

bots = []
for repo in glob.glob("*_bot"):
    module = importlib.import_module(f"{repo}")
    bots.append(module.Bot())

snakes.play(
    bots=bots,  # List of bots to use
    manual=False,  # Set to True to play manually using the keyboard arrow keys
    speedup=1,  # Increase to speed up the game (no guarantees this works very well)
    test=False,  # Set to True to run in test mode
)
