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
    manual=True,  # Set to True to play manually using the keyboard arrow keys
    # music=False,
    # crater_scaling=1.0,  # Artificially increase the size of craters
    # player_collisions=True,  # Set to False to disable collisions between players
    # asteroid_collisions=True,  # Set to False to disable being destroyed by asteroids
    # speedup=1.0,  # Increase to speed up the game (no guarantees this works very well)
    # fullscreen=False,  # Set to True to play in fullscreen mode
    # test=True,  # Set to True to run in test mode
)
