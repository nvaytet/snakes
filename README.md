![banner](https://github.com/user-attachments/assets/8c1010b4-8100-42e6-97b1-aaedb13b8830)

# snakes


## How to

1. Create a repository for your bot from [the template](https://github.com/new?template_name=snake_bot&template_owner=nvaytet).
2. Create a new folder (e.g. name it `pythongame`)
3. Install [pixi](https://pixi.prefix.dev/latest/installation/) if you don't have it installed already
4. Download/copy this [pixi.toml](https://raw.githubusercontent.com/nvaytet/snakes/refs/heads/main/pixi.toml) file into the `pythongame` folder
5. Go inside the game folder and setup the game: `pixi run setup`
6. Run the game: `pixi run play` (SPACEBAR to start a round)
7. Clone your bot into the `pythongame/bots` folder

## Game rules

### Goal

Survive the longest and try to eliminate the others.

### During a round:

- Begin at a random position on the board, heading in a random direction (L, R, U, D)
- If you run into a wall, you die
- If you run into a tail, you die (tails will randomly have gaps)
- Power-up start appearing after a short while


### Power-ups:

<table>
    <tr>
        <td>Decrease thickness<br><img src="https://github.com/user-attachments/assets/b54ba246-835e-4add-ab37-c85e930a4839" /></td>
        <td>Increase thickness<br><img src="https://github.com/user-attachments/assets/9c58a0a0-0d88-4809-8558-6776deb4de45" /></td>
        <td>No tail (can travel through obstacles)<br><img src="https://github.com/user-attachments/assets/281c2728-8476-4dd5-a609-4793cc90b2fa" /></td>
    </tr>
    <tr>
        <td>Increase speed<br><img src="https://github.com/user-attachments/assets/57faa76b-b976-46ea-acac-962b35c1d10a" /></td>
        <td>Decrease speed<br><img src="https://github.com/user-attachments/assets/bdec08de-cfb3-47c4-b7e3-c0f2d40f6c71" /></td>
        <td>Clear board<br><img src="https://github.com/user-attachments/assets/1145aca1-ad69-453d-b385-5004d1c261b9" /></td>
    </tr>
</table>
        


### Scoring:

- Someone else dies: +1 point
- Someone else crashes into your tail: +1 bonus point

### Tournament:

- Reach 100 points to become FINALIST
- After that, you need to WIN one more round to win the match

## The Bot

### Instructions are simple

- `"left"` or `"right"`

### Info you are provided with

- `dt` (float): timestep
- `board` (np.ndarray): 0=empty, nplayers+1=edge, other: player.number
- `players` (dict): team, x, y, direction, speed, score, thickness, number ...
- `powerups` (list): x, y, kind


### Template bot

```Py
import numpy as np


class Bot:
    def __init__(self):
        self.team = "Anaconda"  # This is your team name
        self.rng = np.random.default_rng()

    def run(self, dt, board, players, powerups) -> str | None:
        x = self.rng.random()

        if x < 0.01:
            return "left"
        if x > 0.99:
            return "right"

        # Returning nothing means go straight
        return
```

## Tips

- Use `speedup=3` in `play.py` to speed up your game (results may not exactly reflect a normal round)
- Set `controlling="SomeName"` to control one of the players with the keyboard Left and Right keys
- SPACEBAR during a round pauses the game
- ESCAPE exits the game
