# SPDX-License-Identifier: BSD-3-Clause

import importlib
import snakes

snake_bot = importlib.import_module("../../bots/snake_bot")

names = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Eleanor",
    "Flemming",
    "Greg",
    "Hilde",
    "Isolde",
    "Jack",
    "Kevin",
    "Louis",
    "Marie",
    "Nicholas",
]

bots = []
for name in names:
    bot = snake_bot.Bot()
    bot.team = str(name)
    bots.append(bot)

snakes.play(
    bots=bots,  # List of bots to use
    controlling="Charlie",  # Set name to control player using the keyboard arrow keys
    seed=None,  # Set to an integer to make the game repeatable
    speedup=1,  # Increase to speed up the game (no guarantees this works very well)
)
