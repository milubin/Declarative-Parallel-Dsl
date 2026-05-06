import pygame
import sys
from .settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
                        STATE_EXPLORE, STATE_BATTLE, STATE_DIALOG,
                        STATE_GAMEOVER, STATE_WIN, STATE_LEVELUP,
                        TILESIZE, BLACK, WHITE)
from .maps import VILLAGE, FOREST, DUNGEON, NPC_DATA, ENEMY_DATA, TRANSITIONS, SPAWN_POS, ENEMY_STATS
from .tilemap import TileMap
from .camera  import Camera
from .player  import Player
from .npc     import NPC, Enemy
from .combat  import CombatSystem
from .ui      import (draw_hud, DialogBox, LevelUpScreen,
                       GameOverScreen, WinScreen, TitleScreen)


MAP_DATA = {'village': VILLAGE, 'forest': FOREST, 'dungeon': DUNGEON}


class Game:
    def __init__(self, headless=False):
        self.headless      = headless
        self._quit_flag    = False
        pygame.init()
        if not headless:
            pygame.display.set_caption(TITLE)
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self._load_fonts()
        self.state = 'title'
        self._init_game()

    def _load_fonts(self):
        try:
            self.font_lg = pygame.font.SysFont('arial', 38, bold=True)
            self.font_md = pygame.font.SysFont('arial', 24)
            self.font_sm = pygame.font.SysFont('arial', 18)
        except Exception:
            self.font_lg = pygame.font.Font(None, 40)
            self.font_md = pygame.font.Font(None, 28)
            self.font_sm = pygame.font.Font(None, 22)

    def _init_game(self):
        self.current_map = 'village'
        spawn             = SPAWN_POS[self.current_map]
        self.player       = Player(*spawn)
        self._load_map(self.current_map)
        self.state        = 'title'
        self.combat       = None
        self.title_screen = TitleScreen(self.font_lg, self.font_md, self.font_sm)
        self.dialog_box   = DialogBox(self.font_lg, self.font_md, self.font_sm)
        self.levelup_scr  = LevelUpScreen(self.font_lg, self.font_md, self.font_sm)
        self.gameover_scr = GameOverScreen(self.font_lg, self.font_md, self.font_sm)
        self.win_screen   = WinScreen(self.font_lg, self.font_md, self.font_sm)
        self.tick         = 0
        self.defeated_enemies = set()

    def _load_map(self, name):
        self.current_map = name
        data             = MAP_DATA[name]
        self.tilemap     = TileMap(data)
        self.camera      = Camera(self.tilemap.cols, self.tilemap.rows)

        self.npcs    = []
        for nd in NPC_DATA.get(name, []):
            self.npcs.append(NPC(nd['x'], nd['y'], nd['name'], nd['color'], nd['dialog']))

        self.enemies = []
        for i, ed in enumerate(ENEMY_DATA.get(name, [])):
            key = (name, i)
            if key not in self.defeated_enemies:
                stats = ENEMY_STATS[ed['type']].copy()
                e     = Enemy(ed['x'], ed['y'], ed['type'], stats)
                e._spawn_key = key
                self.enemies.append(e)

    def _transition_map(self, to_map, spawn):
        self._load_map(to_map)
        self.player.set_grid_pos(*spawn)
        self.player.hp = min(self.player.hp + 15, self.player.max_hp)

    def run(self):
        while not self._quit_flag:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            self._handle_events()
            self._update(dt)
            self._draw()

    def step(self, dt):
        """Single-frame update for headless/web mode."""
        self._handle_events()
        self._update(dt)
        self._draw()

    def _quit(self):
        if self.headless:
            self._quit_flag = True
        else:
            pygame.quit()
            sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._quit()
                return

            if self.state == 'title':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = STATE_EXPLORE

            elif self.state == STATE_GAMEOVER:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self._init_game()
                    self.state = STATE_EXPLORE

            elif self.state == STATE_WIN:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self._init_game()
                    self.state = STATE_EXPLORE

            elif self.state == STATE_BATTLE:
                self.combat.handle_event(event)
                if self.combat.result == 'win':
                    if self.combat.phase == 'msg' and event.type == pygame.KEYDOWN and \
                       event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                        leveled = self.player.level > getattr(self, '_prev_level', 1)
                        if self.combat.enemy.is_boss:
                            self.state = STATE_WIN
                        else:
                            self.state = STATE_EXPLORE
                            if leveled:
                                self.levelup_scr.show(self.player.level)
                        self.combat = None
                elif self.combat.result == 'run':
                    if self.combat.phase == 'msg' and event.type == pygame.KEYDOWN and \
                       event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                        self.state  = STATE_EXPLORE
                        self.combat = None
                elif self.combat.result == 'lose':
                    self.state  = STATE_GAMEOVER
                    self.combat = None

            elif self.state == STATE_DIALOG:
                consumed = self.dialog_box.handle_event(event)
                if not self.dialog_box.active:
                    self.state = STATE_EXPLORE

            elif self.state == STATE_EXPLORE:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_RETURN):
                    for npc in self.npcs:
                        if npc.is_adjacent(self.player.rect):
                            self.dialog_box.open(npc.name, npc.dialog)
                            self.state = STATE_DIALOG
                            break

    def _update(self, dt):
        self.tick += 1

        if self.state == 'title':
            self.title_screen.update(dt)
            return

        if self.state == STATE_BATTLE:
            self.combat.update(dt)
            return

        if self.state == STATE_GAMEOVER or self.state == STATE_WIN:
            return

        if self.state == STATE_DIALOG:
            self.dialog_box.update(dt)
            return

        if self.state == STATE_EXPLORE:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys, self.tilemap, dt)
            self.player.update(dt)
            self.camera.update(self.player.rect)
            self.levelup_scr.update(dt)

            for npc in self.npcs:
                npc.update(dt, self.tilemap)

            dead_enemies = []
            for enemy in self.enemies:
                enemy.update(dt, self.tilemap, self.player.rect)
                if enemy.rect.colliderect(self.player.rect):
                    self._prev_level = self.player.level
                    self.combat = CombatSystem(self.player, enemy)
                    self.state  = STATE_BATTLE
                    dead_enemies.append(enemy)
                    if hasattr(enemy, '_spawn_key'):
                        self.defeated_enemies.add(enemy._spawn_key)
                    break

            for e in dead_enemies:
                if e in self.enemies:
                    self.enemies.remove(e)

            self._check_transitions()

    def _check_transitions(self):
        px = self.player.rect.centerx // TILESIZE
        py = self.player.rect.centery // TILESIZE

        for trans in TRANSITIONS.get(self.current_map, []):
            if (px, py) in trans['from_tiles']:
                self._transition_map(trans['to_map'], trans['spawn'])
                return

    def _draw(self):
        self.screen.fill(BLACK)

        if self.state == 'title':
            self.title_screen.draw(self.screen)
            pygame.display.flip()
            return

        if self.state == STATE_GAMEOVER:
            self.gameover_scr.draw(self.screen)
            pygame.display.flip()
            return

        if self.state == STATE_WIN:
            self.win_screen.draw(self.screen, self.player)
            pygame.display.flip()
            return

        if self.state == STATE_BATTLE and self.combat:
            self.combat.draw(self.screen, self.font_lg, self.font_md, self.font_sm)
            pygame.display.flip()
            return

        self.tilemap.draw(self.screen, self.camera, self.tick)

        for npc in self.npcs:
            npc.draw(self.screen, self.camera)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

        self.player.draw(self.screen, self.camera)

        draw_hud(self.screen, self.player, self.font_md, self.font_sm, self.current_map)
        self.levelup_scr.draw(self.screen)

        if self.state == STATE_DIALOG:
            self.dialog_box.draw(self.screen)

        pygame.display.flip()
