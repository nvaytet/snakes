# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional

import numpy as np
import pyglet
import time

from . import config
from .powerup import all_powerups

from .graphics import Graphics
from .player import Player
from .scores import read_scores, finalize_scores
from .tools import Instructions, PlayerInfo, PowerupInfo


def add_key_actions(window, player: Player):
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            player.turn_left()
        elif symbol == pyglet.window.key.RIGHT:
            player.turn_right()


class Engine:
    def __init__(
        self,
        bots: list,
        safe: bool = False,
        test: bool = True,
        seed: Optional[int] = None,
        fullscreen: bool = False,
        manual: bool = False,
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
        scores = read_scores(self.bots, test=test)

        self.reset_board()

        self.players = {}
        for i, team in enumerate(self.bots):
            xpos = np.random.uniform(0, config.nx - 1)
            ypos = np.random.uniform(0, config.ny - 1)
            self.players[team] = Player(
                team=team,
                number=i + 1,
                position=(xpos, ypos),
                score=scores[team],
            )

        self.graphics = Graphics(fullscreen=fullscreen, players=self.players)

        for player in self.active_players():
            player.make_avatar(batch=self.graphics.main_batch)

        self.graphics.update_scores(players=self.players)

        if manual:
            manual_player = list(self.players.values())[0]
            self._manual = manual_player.team
            add_key_actions(window=self.graphics.window, player=manual_player)
        else:
            self._manual = None

        self.start_time = time.time()
        self.time = 0.0

        pyglet.clock.schedule_interval(self.update, 1 / config.fps)
        pyglet.app.run()

    def reset_board(self):
        nplayers = len(self.bots)
        self.board_old = np.zeros((config.ny, config.nx), dtype=np.uint8)
        self.board_old[0, :] = nplayers + 1
        self.board_old[-1, :] = nplayers + 1
        self.board_old[:, 0] = nplayers + 1
        self.board_old[:, -1] = nplayers + 1
        self.board_new = self.board_old.copy()

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

    def active_players(self):
        return (p for p in self.players.values() if not p.dead)

    def execute_player_bot(self, team: str, info: dict) -> Instructions:
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
        info = {"dt": dt, "board": self.board_new.copy()}
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
        for player in self.active_players():
            old = player.position()
            player.move(dt=dt)
            new = player.position()
            hw = (player.thickness - 1) // 2
            ystart = min(old[1], new[1]) - hw
            yend = max(old[1], new[1]) + 1 + hw
            xstart = min(old[0], new[0]) - hw
            xend = max(old[0], new[0]) + 1 + hw
            ystart = np.clip(ystart, 0, config.ny)
            yend = np.clip(yend, 0, config.ny)
            xstart = np.clip(xstart, 0, config.nx)
            xend = np.clip(xend, 0, config.nx)

            if not player.ghost and not player.gap:
                self.board_new[ystart:yend, xstart:xend] = player.number

            patch = self.board_old[ystart:yend, xstart:xend]
            if (patch.sum() > (player.number * player.thickness**2)) and (
                not player.invincible and (not player.ghost) and (player.gap == 0)
            ):
                player.die()
                points += 1
                clipped = np.where(patch == 0, np.nan, patch)
                patch_min = int(np.nanmin(clipped))
                patch_max = int(np.nanmax(clipped))
                bonus.append(patch_min if patch_max == player.number else patch_max)

        self.board_old[...] = self.board_new[...]
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
            player.invincible = False
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

    def update_player_gap_state(self, t: float):
        for player in self.active_players():
            if player.gap:
                if t > player.gap:
                    player.gap = 0
                    player.next_gap = t + np.random.uniform(0, config.gap_period)
            elif t > player.next_gap:
                player.gap = t + config.gap_duration

    def update(self, dt: float):
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
        self.graphics.update(array=self.board_old)

        players_left = list(self.active_players())
        if len(players_left) < 2:
            self.exit(last_player=players_left[0] if players_left else None)

        return
