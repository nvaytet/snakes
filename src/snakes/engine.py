# SPDX-License-Identifier: BSD-3-Clause

import time
from typing import Iterator

import numpy as np
import pyglet
from pyglet.window import Window

from . import config
from .graphics import Graphics
from .player import Player, PlayerInfo
from .powerup import PowerupInfo, all_powerups
from .scores import finalize_scores, read_scores


class Engine:
    def __init__(
        self,
        bots: list,
        safe: bool = False,
        test: bool = True,
        seed: int | None = None,
        controlling: str | None = None,
        speedup: int = 1,
    ):
        if seed is not None:
            np.random.seed(seed)

        self._test = test
        self.safe = safe
        self.match_winner = False
        self.round_winner = False
        self.speedup = int(speedup)
        self.powerups = []
        self.bots = {bot.team: bot for bot in bots}
        self.paused = True
        scores = read_scores(self.bots, test=test)

        self.board = np.zeros((config.ny, config.nx), dtype=np.uint8)
        self.turn_mask = np.zeros((config.ny, config.nx), dtype=np.uint8)
        self.reset_board()

        self.players = {}
        pad = 20
        for i, team in enumerate(self.bots):
            xpos = np.random.uniform(pad, config.nx - pad - 1)
            ypos = np.random.uniform(pad, config.ny - pad - 1)
            self.players[team] = Player(
                team=team,
                number=i + 1,
                position=(xpos, ypos),
                score=scores[team],
            )
            print(f"Player {team} has number {i + 1} {self.players[team].number}")

        self.graphics = Graphics(players=self.players)

        for player in self.active_players():
            player.make_avatar(batch=self.graphics.main_batch)

        self.graphics.update_scores(players=self.players)

        if controlling:
            manual_player = self.players[controlling]
            self._manual = manual_player.team
        else:
            self._manual = None

        add_key_actions(
            window=self.graphics.window,
            player=self.players.get(controlling),
            engine=self,
        )

        self.start_time = time.time()
        self.time = 0.0

        pyglet.clock.schedule_interval(self.update, 1 / config.fps)
        pyglet.app.run()

    def reset_board(self):
        nplayers = len(self.bots)
        self.board[...] = 0
        self.board[0, :] = nplayers + 1
        self.board[-1, :] = nplayers + 1
        self.board[:, 0] = nplayers + 1
        self.board[:, -1] = nplayers + 1
        # self.board_new = self.board.copy()

    def exit(self, last_player: Player | None):
        if last_player is not None:
            if last_player.finalist:
                last_player.score = config.high_score * 20
                self.match_winner = f"{last_player.team} wins the match!"
            else:
                self.round_winner = f"{last_player.team} wins the round!"
        else:
            self.round_winner = "It's a draw!"

        finalize_scores(players=self.players, test=self._test)

    def active_players(self) -> Iterator[Player]:
        return (p for p in self.players.values() if not p.dead)

    def execute_player_bot(self, team: str, info: dict) -> str | None:
        instructions = None
        if self.safe:
            try:
                instructions = self.bots[team].run(**info)
            except:  # noqa
                pass
        else:
            instructions = self.bots[team].run(**info)
        return instructions

    def call_player_bots(self, dt: float):
        info = {"dt": dt, "board": self.board.copy()}
        info["players"] = {
            team: PlayerInfo(**p.to_dict()) for team, p in self.players.items()
        }
        info["powerups"] = [PowerupInfo(**p.to_dict()) for p in self.powerups]
        for player in (p for p in self.active_players() if p.team != self._manual):
            if self.safe:
                try:
                    player.execute_bot_instructions(
                        self.execute_player_bot(team=player.team, info=info)
                    )
                except:  # noqa
                    pass
            else:
                player.execute_bot_instructions(
                    self.execute_player_bot(team=player.team, info=info)
                )

    def move_players(self, dt: float):
        points = 0
        bonus = []
        board_updates = []
        for player in self.active_players():
            old = player.position()
            player.move(dt=dt)
            new = player.position()
            hw = (player.thickness - 1) // 2
            # if player.direction == "U":
            #     obstacle = (new[0] - hw, new[0] + hw + 1, old[1] - hw, new[1] + hw + 1)
            #     tail = (new[0] - hw, new[0] + hw + 1, old[1] - hw, new[1])
            # elif player.direction == "D":
            #     obstacle = (new[0] - hw, new[0] + hw + 1, new[1] - hw, old[1] + hw + 1)
            #     tail = (new[0] - hw, new[0] + hw + 1, new[1] + 1, old[1] + hw + 1)
            # elif player.direction == "L":
            #     obstacle = (new[0] - hw, old[0] + hw + 1, new[1] - hw, new[1] + hw + 1)
            #     tail = (new[0] + 1, old[0] + hw + 1, new[1] - hw, new[1] + hw + 1)
            # elif player.direction == "R":
            #     obstacle = (old[0] - hw, new[0] + hw + 1, new[1] - hw, new[1] + hw + 1)
            #     tail = (old[0] - hw, new[0], new[1] - hw, new[1] + hw + 1)

            # if player.direction == "U":
            #     obstacle = (new[0] - hw, new[0] + hw + 1, old[1], new[1] + 1)
            # elif player.direction == "D":
            #     obstacle = (new[0] - hw, new[0] + hw + 1, new[1], old[1] + 1)
            # elif player.direction == "L":
            #     obstacle = (new[0], old[0] + 1, new[1] - hw, new[1] + hw + 1)
            # elif player.direction == "R":
            #     obstacle = (old[0], new[0] + 1, new[1] - hw, new[1] + hw + 1)

            if player.direction == "U":
                obstacle = (new[0] - hw, new[0] + hw + 1, old[1], new[1])
            elif player.direction == "D":
                obstacle = (new[0] - hw, new[0] + hw + 1, new[1], old[1])
            elif player.direction == "L":
                obstacle = (new[0], old[0], new[1] - hw, new[1] + hw + 1)
            elif player.direction == "R":
                obstacle = (old[0], new[0], new[1] - hw, new[1] + hw + 1)

            tail = obstacle

            obstacle = (
                *np.clip(obstacle[0:2], 0, config.nx),
                *np.clip(obstacle[2:], 0, config.ny),
            )
            tail = (*np.clip(tail[0:2], 0, config.nx), *np.clip(tail[2:], 0, config.ny))

            if not player.ghost and not player.gap:
                # self.board_new[tail[2] : tail[3], tail[0] : tail[1]] = player.number
                board_updates.append(
                    {
                        "slice": (slice(tail[2], tail[3]), slice(tail[0], tail[1])),
                        "value": player.number,
                    }
                )

            patch = self.board[obstacle[2] : obstacle[3], obstacle[0] : obstacle[1]]
            # if (patch.sum() > (player.number * player.thickness**2)) and (
            #     not player.invincible and (not player.ghost) and (player.gap == 0)
            # ):
            # print(
            #     f"Player {player.team}, pos: {new},  patch sum: {patch.sum()} number: {player.number}"
            # )
            # print("patch bounds", obstacle[0], obstacle[1], obstacle[2], obstacle[3])
            if (
                # (patch.sum() > (player.number * player.thickness**2))
                (patch.sum() > 0) and (not player.ghost) and (player.gap == 0)
            ):
                player.die()
                points += 1
                clipped = np.where(patch == 0, np.nan, patch)
                patch_min = int(np.nanmin(clipped))
                patch_max = int(np.nanmax(clipped))
                bonus.append(patch_min if patch_max == player.number else patch_max)

        # self.board[...] = self.board_new[...]

        # Synchronized upate
        for update in board_updates:
            self.board[update["slice"]] = update["value"]

        if points > 0:
            for player in [p for p in self.active_players() if not p.finalist]:
                player.score += points
                if player.number in bonus:
                    player.score += 1
            self.graphics.update_scores(players=self.players)

    def make_powerups(self, t: float):
        if (len(self.powerups) >= config.max_powerups) or (
            t < config.no_powerups / self.speedup
        ):
            return
        x, y = np.random.uniform(0, config.nx - 1), np.random.uniform(0, config.ny - 1)
        powerup = np.random.choice(
            list(all_powerups.keys()), p=list(all_powerups.values())
        )
        self.powerups.append(
            powerup(x=x, y=y, speedup=self.speedup, batch=self.graphics.main_batch)
        )

    def get_powerups(self):
        for player in self.active_players():
            # player.invincible = False
            for powerup in self.powerups:
                dist = np.linalg.norm(
                    np.array([player.x, player.y]) - np.array([powerup.x, powerup.y])
                )
                if dist < (config.powerup_size / 2):
                    if powerup.kind == "clear":
                        self.reset_board()
                    else:
                        powerup.apply(player)
                        player.powerups.append(powerup)
                    self.powerups.remove(powerup)

    def expire_powerups(self):
        for player in self.active_players():
            for pup in player.powerups:
                pup.tick()
                if pup.is_expired():
                    pup.revert(player)
                    player.powerups.remove(pup)
        for powerup in list(self.powerups):
            powerup.age()
            if powerup.lifetime <= 0:
                powerup.avatar.delete()
                self.powerups.remove(powerup)

    def update_player_gap_state(self, t: float):
        for player in self.active_players():
            if player.gap:
                if t > player.gap:
                    player.gap = 0
                    player.next_gap = t + np.random.uniform(0, config.gap_period)
            elif t > player.next_gap:
                player.gap = t + config.gap_duration

    def update(self, dt: float):
        if self.paused:
            self.graphics.show_player_names(self.players)
            return
        else:
            self.graphics.hide_player_names()
        dt = dt * self.speedup
        self.time += dt
        if self.match_winner:
            if self.graphics.exit_message is None:
                self.graphics.show_exit_message(self.match_winner)
            return
        if self.round_winner:
            if self.graphics.exit_message is None:
                self.graphics.show_exit_message(self.round_winner)
            return

        self.update_player_gap_state(self.time)
        self.expire_powerups()
        self.make_powerups(self.time)
        self.call_player_bots(dt)
        self.move_players(dt=dt)
        self.get_powerups()
        self.graphics.update(array=self.board)

        players_left = list(self.active_players())
        if len(players_left) < 2:
            self.exit(last_player=players_left[0] if players_left else None)

        return


def add_key_actions(window: Window, player: Player | None, engine: Engine):
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            if player is not None:
                player.turn_left()
        elif symbol == pyglet.window.key.RIGHT:
            if player is not None:
                player.turn_right()
        elif symbol == pyglet.window.key.SPACE:
            engine.paused = not engine.paused
