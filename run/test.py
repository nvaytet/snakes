# SPDX-License-Identifier: BSD-3-Clause


import snakes

import template_bot

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
    bot = template_bot.Bot()
    bot.team = name
    bots.append(bot)

snakes.play(
    bots=bots,  # List of bots to use
    manual=False,  # Set to True to play manually using the keyboard arrow keys
    test=False,
    speedup=1,  # Increase to speed up the game (no guarantees this works very well)
)
