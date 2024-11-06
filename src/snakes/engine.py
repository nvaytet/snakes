# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional

import numpy as np
import pyglet
import time

from . import config
from .powerup import ThinPowerup

# from .asteroid import Asteroid
from .graphics import Graphics
from .player import Player

# from .scores import finalize_scores
# from .terrain import Terrain
from .tools import Instructions, PlayerInfo


def add_key_actions(window, player: Player):
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            player.turn_left()
        elif symbol == pyglet.window.key.RIGHT:
            player.turn_right()

    # @window.event
    # def on_key_release(symbol, modifiers):
    #     if symbol == pyglet.window.key.UP:
    #         player.main_thruster = False
    #     elif symbol == pyglet.window.key.LEFT:
    #         player.left_thruster = False
    #     elif symbol == pyglet.window.key.RIGHT:
    #         player.right_thruster = False


class Engine:
    def __init__(
        self,
        bots: list,
        safe: bool = False,
        test: bool = True,
        seed: Optional[int] = None,
        fullscreen: bool = False,
        manual: bool = False,
        crater_scaling: float = 1.0,
        player_collisions: bool = True,
        asteroid_collisions: bool = True,
        speedup: float = 1.0,
    ):
        if seed is not None:
            np.random.seed(seed)

        nplayers = len(bots)

        # config.nx = config.nx
        # config.ny = config.ny
        self.board_old = np.zeros((config.ny, config.nx), dtype=np.uint8)
        self.board_old[0, :] = nplayers + 1
        self.board_old[-1, :] = nplayers + 1
        self.board_old[:, 0] = nplayers + 1
        self.board_old[:, -1] = nplayers + 1
        self.board_new = self.board_old.copy()
        # self.start_time = None
        # self._test = test
        # self.asteroids = []
        self.safe = safe
        self.exiting = False
        # self.time_of_last_scoreboard_update = 0
        # self.time_of_last_asteroid = 0
        # self._crater_scaling = crater_scaling
        # self._player_collisions = player_collisions
        # self._asteroid_collisions = asteroid_collisions
        # self._speedup = speedup

        # self.game_map = Terrain()

        # colors = []
        # cmap = plt.get_cmap("gist_ncar")
        # nplayers = len(bots) + 1
        # for i in range(nplayers):
        #     colors.append(cmap(i / (nplayers - 1)))

        self.powerups = []

        self.bots = {bot.team: bot for bot in bots}
        # starting_positions = self.make_starting_positions(nplayers=len(self.bots))
        self.players = {}
        for i, team in enumerate(self.bots):
            # for i in range(nplayers):
            xpos = np.random.uniform(0, config.nx - 1)
            ypos = np.random.uniform(0, config.ny - 1)
            # xpos = 10
            # ypos = 10
            # team = bot.team
            # team = f"Player {i + 1}"
            self.players[team] = Player(
                team=team,
                number=i + 1,
                # color=colors[i + 1],
                position=(xpos, ypos),
                # avatar=getattr(bot, "avatar", 0),
                # back_batch=self.graphics.background_batch,
                # main_batch=self.graphics.main_batch,
            )

        self.graphics = Graphics(fullscreen=fullscreen, players=self.players)

        if manual:
            manual_player = list(self.players.values())[0]
            self._manual = manual_player.team
            add_key_actions(window=self.graphics.window, player=manual_player)
        else:
            self._manual = None

        self.start_time = time.time()

        pyglet.clock.schedule_interval(self.update, 1 / config.fps)
        pyglet.app.run()

    # def make_starting_positions(self, nplayers: int) -> list:
    #     random_origin = np.random.uniform(0, config.nx)
    #     step = config.nx / nplayers
    #     choices = [int(random_origin + i * step) % config.nx for i in range(nplayers)]
    #     return np.random.permutation(choices)

    # def exit(self, message: str):
    #     self.exiting = True
    #     print(message)
    #     # finalize_scores(players=self.players, test=self._test)

    def active_players(self):
        return (p for p in self.players.values() if not p.dead)

    # def generate_info(self, dt: float) -> dict:
    #     info = {"dt": dt, "board": self.game_map.terrain}
    #     info["players"] = {
    #         team: PlayerInfo(**p.to_dict()) for team, p in self.players.items()
    #     }
    #     info["asteroids"] = [AsteroidInfo(**a.to_dict()) for a in self.asteroids]
    #     return info

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
        # info = self.generate_info(t=t, dt=dt)
        info = {"dt": dt, "board": self.board_new}
        info["players"] = {
            team: PlayerInfo(**p.to_dict()) for team, p in self.players.items()
        }
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
        bonus = 0
        for player in self.active_players():
            old = player.position()
            player.move(dt=dt)
            new = player.position()
            # self.board_old[pos[1], pos[0]] = player.number
            hw = (player.thickness - 1) // 2
            ystart = min(old[1], new[1]) - hw
            yend = max(old[1], new[1]) + 1 + hw
            # if ystart != yend - 1:
            #     ystart += 1
            # yplus = 0
            # else:
            #     yplus = 1
            xstart = min(old[0], new[0]) - hw
            xend = max(old[0], new[0]) + 1 + hw
            # if xstart != xend - 1:
            #     xstart += 1
            #     xplus = 0
            # else:
            #     xplus = 1
            # ystart = min(max(0, ystart), config.ny)
            # yend = min(max(0, yend), config.ny)
            # xstart = min(max(0, xstart), config.nx)
            # xend = min(max(0, xend), config.nx)
            ystart = np.clip(ystart, 0, config.ny)
            yend = np.clip(yend, 0, config.ny)
            xstart = np.clip(xstart, 0, config.nx)
            xend = np.clip(xend, 0, config.nx)

            # # if (xend - 1 - xstart) + (yend - 1 - ystart) > 0:
            # yplus = int(ystart != yend - 1)
            # y1 = yplus and ((yend - 1) == new[1])
            # y2 = yplus and (ystart == new[1])
            # xplus = int(xstart != xend - 1)
            # x1 = xplus and ((xend - 1) == new[0])
            # x2 = xplus and (xstart == new[0])

            self.board_new[ystart:yend, xstart:xend] = player.number
            patch = self.board_old[ystart:yend, xstart:xend]
            if patch.sum() > player.number * player.thickness**2:
                player.die()
                points += 1
                clipped = np.clip(patch, 1, len(self.players))
                patch_min = clipped.min()
                patch_max = clipped.max()
                bonus = patch_min if patch_max == player.number else patch_max

        self.board_old[...] = self.board_new[...]
        if points > 0:
            for player in self.active_players():
                player.score += points
                if player.number == bonus:
                    player.score += 1

    def make_powerups(self, t: float):
        if self.powerups:
            return
        # print("making powerup")
        x, y = np.random.uniform(0, config.nx - 1), np.random.uniform(0, config.ny - 1)
        self.powerups.append(ThinPowerup(x=x, y=y, batch=self.graphics.main_batch))

    def get_powerups(self):
        for player in self.active_players():
            for powerup in self.powerups:
                if (
                    np.linalg.norm(
                        np.array([player.x, player.y])
                        - np.array([powerup.x, powerup.y])
                    )
                    < config.powerup_size
                ):
                    powerup.apply(player)
                    # powerup.avatar.delete()
                    self.powerups.remove(powerup)

    # def check_landing(self, t: float):
    #     for player in self.active_players():
    #         lem_floor = int(player.y - config.avatar_size[1] / 2)
    #         y_values = self.game_map.terrain[
    #             int(player.x - config.avatar_size[0] / 2) : int(
    #                 player.x + config.avatar_size[0] / 2
    #             ),
    #         ]
    #         if any(y_values >= lem_floor):
    #             uneven_terrain = any(y_values < lem_floor)
    #             too_fast = np.linalg.norm(player.velocity) > config.max_landing_speed
    #             landing_angle = np.abs(player.heading)
    #             bad_angle = landing_angle > config.max_landing_angle
    #             if any([uneven_terrain, too_fast, bad_angle]):
    #                 reason = []
    #                 if uneven_terrain:
    #                     reason.append("uneven terrain")
    #                 if too_fast:
    #                     reason.append(
    #                         f"velocity=[{player.velocity[0]:.1f}, "
    #                         f"{player.velocity[1]:.1f}]"
    #                     )
    #                 if bad_angle:
    #                     reason.append(f"landing angle={landing_angle:.1f}")
    #                 player.crash(reason=", ".join(reason))
    #             else:
    #                 player.land(
    #                     time_left=config.time_limit - t,
    #                     landing_site_width=self.game_map.landing_sites[int(player.x)],
    #                     flag=getattr(self.bots[player.team], "flag", None),
    #                 )

    # def compute_collisions(self):
    #     players = list(self.active_players())
    #     n = len(players)
    #     x = np.array([p.x for p in players])
    #     y = np.array([p.y for p in players])
    #     xpos1 = np.broadcast_to(x, (n, n))
    #     xpos2 = xpos1.T
    #     ypos1 = np.broadcast_to(y, (n, n))
    #     ypos2 = ypos1.T
    #     dist = np.tril(np.sqrt((xpos2 - xpos1) ** 2 + (ypos2 - ypos1) ** 2))
    #     lems1, lems2 = np.where((dist < config.collision_radius) & (dist > 0))
    #     for i, j in zip(lems1, lems2):
    #         p1 = players[i]
    #         p2 = players[j]
    #         x1 = p1.position
    #         v1 = p1.velocity
    #         x2 = p2.position
    #         v2 = p2.velocity
    #         p1.velocity = v1 - np.dot(v1 - v2, x1 - x2) / np.linalg.norm(
    #             x1 - x2
    #         ) ** 2 * (x1 - x2)
    #         p2.velocity = v2 - np.dot(v2 - v1, x2 - x1) / np.linalg.norm(
    #             x2 - x1
    #         ) ** 2 * (x2 - x1)

    # def update_asteroids(self, t: float, dt: float):
    #     delay = (
    #         1.0 - config.asteroid_delay
    #     ) / config.time_limit * t + config.asteroid_delay
    #     if (t - self.time_of_last_asteroid) > delay:
    #         self.asteroids.append(
    #             Asteroid(
    #                 x=np.random.uniform(0, config.nx),
    #                 y=config.ny + 100,
    #                 v=np.random.uniform(100, 200),
    #                 heading=np.random.uniform(-25, -155),
    #                 size=72,
    #                 batch=self.graphics.main_batch,
    #             )
    #         )
    #         self.time_of_last_asteroid = t
    #     for asteroid in self.asteroids:
    #         asteroid.move(dt=dt)
    #         tip = asteroid.tip()
    #         tip_size = asteroid.size * config.asteroid_tip_size
    #         if self._asteroid_collisions:
    #             for player in self.active_players():
    #                 d = np.sqrt((player.x - tip[0]) ** 2 + (player.y - tip[1]) ** 2)
    #                 if d < tip_size:
    #                     player.crash(reason="asteroid collision")
    #         if tip[1] <= self.game_map.terrain[int(tip[0])]:
    #             self.game_map.make_crater(x=int(tip[0]), scaling=self._crater_scaling)
    #             asteroid.avatar.delete()
    #             self.asteroids.remove(asteroid)

    def update(self, dt: float):
        t = time.time() - self.start_time
        if self.exiting:
            if self.graphics.exit_message is None:
                self.graphics.show_exit_message()
            return

        # dt = dt * self._speedup
        self.make_powerups(t)
        self.call_player_bots(dt)
        self.move_players(dt=dt)
        self.get_powerups()
        # self.check_landing(t=t)
        # if self._player_collisions:
        #     self.compute_collisions()
        # self.update_asteroids(t, dt)
        self.graphics.update(array=self.board_old, players=self.players)

        if len(list(self.active_players())) < 2:
            self.exiting = True
            # self.exit()

        return
