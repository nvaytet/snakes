# SPDX-License-Identifier: BSD-3-Clause

import snake_bot
import snakes

names = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Eleanor",
    "Flemming",
    "Greg",
]

bots = []
for name in names:
    bot = snake_bot.Bot()
    bot.team = name
    bots.append(bot)

snakes.play(
    bots=bots,  # List of bots to use
    manual=True,  # Set to True to play manually using the keyboard arrow keys
    seed=None,  # Set to an integer to make the game repeatable
    speedup=1,  # Increase to speed up the game (no guarantees this works very well)
)
