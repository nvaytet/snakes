![banner](https://github.com/user-attachments/assets/8c1010b4-8100-42e6-97b1-aaedb13b8830)

# snakes


## TL;DR

1. Create a repository for your bot from [the template](https://github.com/new?template_name=snake_bot&template_owner=nvaytet).

2. Get started with:

### conda

```
conda create -n <ENVNAME> -c conda-forge python=3.10.*
conda activate <ENVNAME>
git clone https://github.com/nvaytet/snakes.git
git clone https://github.com/<USERNAME>/<MYPLAYERNAME>_bot.git
cd snakes/
python -m pip install -e .
cd run/
ln -s ../../<MYPLAYERNAME>_bot .
python play.py
```

### venv

```
git clone https://github.com/nvaytet/snakes.git
git clone https://github.com/<USERNAME>/<MYPLAYERNAME>_bot.git
cd snakes/
python -m venv .<ENVNAME>
source .<ENVNAME>/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
cd run/
ln -s ../../<MYPLAYERNAME>_bot .
python play.py
```

## Game rules

### Goal

Survive the longest and try to eliminate the others.

### During a round:

- Begin at a random position on the board, heading in a random direction (L, R, U, D)
- If you run into a wall, you die
- If you run into a tail, you die (tails will randomly have gaps)
- Power-up start appearing after a short while


### Power-ups:



### Scoring:

- Someone else dies: +1 point
- Someone else crashes into your tail: +1 bonus point

### Tournament:

- Reach 100 points to become FINALIST
- After that, you need to WIN one more round to win the match

## The Bot

### Instructions are simple

- **LEFT** or **RIGHT**

### Info you are provided with

- `dt` (float): timestep
- `board` (np.ndarray): 0=empty, nplayers+1=edge, other: player.number
- `players` (dict): team, x, y, direction, speed, score, thickness, number ...
- `powerups` (list): x, y, kind


### Template bot

```Py
import numpy as np

from snakes import Instructions


class Bot:
    def __init__(self):
        self.team = "Anaconda"  # This is your team name

    def run(self, dt, board, players, powerups) -> Instructions:
        instructions = Instructions()

        me = players[self.team]

        # Projected position: check what is N pixels ahead?
        n = 8
        hwidth = (me.thickness - 1) // 2
        x = int(me.x)
        y = int(me.y)

        bounds = {
            "U": (x, x + 1, y + hwidth + 1, y + n + 1),
            "D": (x, x + 1, y - n, y - hwidth),
            "L": (x - n, x - hwidth, y, y + 1),
            "R": (x + hwidth + 1, x + n + 1, y, y + 1),
        }

        xmin, xmax, ymin, ymax = bounds[me.direction]
        xmin, xmax = np.clip([xmin, xmax], 0, board.shape[1])
        ymin, ymax = np.clip([ymin, ymax], 0, board.shape[0])

        if np.any(board[ymin:ymax, xmin:xmax] > 0):
            instructions.left = True

        return instructions
```

## Tips

- Use `speedup=3` to speed up your game (results may not exactly reflect a normal round)
