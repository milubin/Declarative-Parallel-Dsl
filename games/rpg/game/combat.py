import pygame
import random
from .settings import (SCREEN_WIDTH, SCREEN_HEIGHT, TILESIZE,
                        BLACK, WHITE, RED, DARK_RED, GREEN, BLUE, YELLOW, GOLD,
                        DARK_GRAY, GRAY, LIGHT_GRAY, BROWN, ORANGE, PURPLE,
                        CREAM, DIR_DOWN)
from .npc import draw_enemy_sprite


PANEL_H   = 200
PANEL_Y   = SCREEN_HEIGHT - PANEL_H
BG_COL    = (20, 18, 25)
PANEL_COL = (30, 27, 35)
BORDER    = (80, 60, 100)


class CombatSystem:
    def __init__(self, player, enemy):
        self.player       = player
        self.enemy        = enemy
        self.phase        = 'choose'
        self.message      = f"A wild {enemy.name} appeared!"
        self.log          = []
        self.selected     = 0
        self.actions      = ['Attack', 'Magic', 'Heal', 'Run']
        self.result       = None
        self.anim_tick    = 0
        self.shake        = 0
        self.flash_player = False
        self.flash_enemy  = False
        self.enemy_frame  = 0
        self.enemy_tick   = 0

    def handle_event(self, event):
        if self.phase != 'choose':
            if self.phase == 'msg':
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                    self.phase = 'choose'
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(self.actions)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(self.actions)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 2) % len(self.actions)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 2) % len(self.actions)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._execute_action(self.actions[self.selected])

    def _execute_action(self, action):
        p = self.player
        e = self.enemy

        if action == 'Attack':
            base_dmg = p.atk + random.randint(-2, 4)
            dmg      = max(1, base_dmg - e.defense)
            crit     = random.random() < 0.15
            if crit:
                dmg = int(dmg * 1.8)
            e.hp = max(0, e.hp - dmg)
            msg  = f"You deal {dmg} damage" + (" — CRITICAL!" if crit else "!")
            self.flash_enemy = True
            self.shake       = 8

        elif action == 'Magic':
            if p.mp < 8:
                self.message = "Not enough MP!"
                self.phase   = 'msg'
                return
            p.mp -= 8
            dmg   = p.magic * 2 + random.randint(2, 8)
            e.hp  = max(0, e.hp - dmg)
            msg   = f"Magic blast! {dmg} damage!"
            self.flash_enemy = True

        elif action == 'Heal':
            if p.mp < 12:
                self.message = "Not enough MP!"
                self.phase   = 'msg'
                return
            p.mp  -= 12
            heal   = int(p.max_hp * 0.3) + random.randint(0, 10)
            p.heal(heal)
            msg    = f"You restore {heal} HP!"
            self.flash_player = True

        elif action == 'Run':
            chance = 0.55
            if random.random() < chance:
                self.result  = 'run'
                self.message = "You fled safely!"
                self.phase   = 'msg'
                return
            else:
                msg = "Couldn't escape!"
                self._enemy_turn()
                self.message = msg + " " + self.log[-1] if self.log else msg
                self.phase   = 'msg'
                return

        self.log.append(msg)
        if e.hp <= 0:
            leveled  = p.gain_exp(e.exp_reward)
            end_msg  = f"{e.name} defeated! +{e.exp_reward} EXP"
            if leveled:
                end_msg += f"  LEVEL UP! Now Lv.{p.level}!"
            self.message = end_msg
            self.result  = 'win'
            self.phase   = 'msg'
            return

        self._enemy_turn()
        full_msg = msg
        if self.log:
            full_msg += "  " + self.log[-1]
        self.message = full_msg
        self.phase   = 'msg'

        if p.hp <= 0:
            self.result = 'lose'

    def _enemy_turn(self):
        p    = self.player
        e    = self.enemy
        dmg  = max(1, e.atk + random.randint(-2, 3) - p.defense)
        crit = random.random() < 0.1
        if crit:
            dmg = int(dmg * 1.7)
        p.take_damage(dmg + p.defense)
        self.flash_player = True
        msg = f"{e.name} hits you for {dmg}" + (" — CRITICAL!" if crit else "!")
        self.log.append(msg)

    def update(self, dt):
        self.anim_tick += dt
        self.enemy_tick += dt
        self.enemy_frame = int(self.enemy_tick * 5) % 4
        if self.shake > 0:
            self.shake -= 1
        if self.anim_tick > 0.3:
            self.flash_player = False
            self.flash_enemy  = False

    def draw(self, screen, font_lg, font_md, font_sm):
        screen.fill(BG_COL)

        ew = TILESIZE * 3
        eh = TILESIZE * 3
        ex = SCREEN_WIDTH // 2 - ew // 2
        ey = SCREEN_HEIGHT // 2 - eh - 40

        shake_ox = random.randint(-self.shake, self.shake) if self.shake else 0
        enemy_r  = pygame.Rect(ex + shake_ox, ey, ew, eh)

        if not self.flash_enemy:
            enemy_surf = pygame.Surface((ew, eh), pygame.SRCALPHA)
            draw_enemy_sprite(enemy_surf, pygame.Rect(0, 0, ew, eh),
                              self.enemy.etype, self.enemy_frame, self.enemy.hp_ratio())
            screen.blit(enemy_surf, enemy_r)
        else:
            pygame.draw.rect(screen, (255, 255, 255), enemy_r, border_radius=4)

        name_surf = font_lg.render(self.enemy.name, True, WHITE)
        screen.blit(name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, ey - 32))

        _draw_bar(screen, ex, ey - 14, ew, 10,
                  self.enemy.hp, self.enemy.max_hp, (200,40,40), (60,180,60))

        panel = pygame.Rect(0, PANEL_Y - 10, SCREEN_WIDTH, PANEL_H + 10)
        pygame.draw.rect(screen, PANEL_COL, panel)
        pygame.draw.rect(screen, BORDER,    panel, 2)

        msg_lines = _wrap_text(self.message, font_md, SCREEN_WIDTH - 40)
        for i, line in enumerate(msg_lines[:3]):
            s = font_md.render(line, True, CREAM)
            screen.blit(s, (20, PANEL_Y + 6 + i * 26))

        if self.phase == 'choose':
            btn_w, btn_h = 140, 44
            cols, rows   = 2, 2
            start_x      = SCREEN_WIDTH // 2 - (cols * (btn_w + 10)) // 2
            start_y      = PANEL_Y + 90

            for i, act in enumerate(self.actions):
                col  = i % cols
                row  = i // cols
                bx   = start_x + col * (btn_w + 10)
                by   = start_y + row * (btn_h + 8)
                sel  = (i == self.selected)
                bcol = (80, 60, 110) if sel else (45, 40, 55)
                bdcol= GOLD         if sel else BORDER
                pygame.draw.rect(screen, bcol,  (bx, by, btn_w, btn_h), border_radius=6)
                pygame.draw.rect(screen, bdcol, (bx, by, btn_w, btn_h), border_radius=6, width=2)
                tc   = GOLD if sel else LIGHT_GRAY
                ts   = font_md.render(act, True, tc)
                screen.blit(ts, (bx + btn_w//2 - ts.get_width()//2,
                                 by + btn_h//2 - ts.get_height()//2))
        elif self.phase == 'msg':
            hint = font_sm.render("Press ENTER / SPACE to continue", True, GRAY)
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, PANEL_Y + 165))

        _draw_player_hud(screen, font_sm, self.player, self.flash_player)


def _draw_bar(screen, x, y, w, h, val, maxval, bg_col, fg_col):
    pygame.draw.rect(screen, bg_col, (x, y, w, h), border_radius=3)
    filled = int(w * (val / maxval)) if maxval > 0 else 0
    if filled > 0:
        pygame.draw.rect(screen, fg_col, (x, y, filled, h), border_radius=3)
    pygame.draw.rect(screen, LIGHT_GRAY, (x, y, w, h), border_radius=3, width=1)


def _draw_player_hud(screen, font, player, flash):
    p  = player
    bx = 12
    by = PANEL_Y - 60

    bg = pygame.Surface((220, 52), pygame.SRCALPHA)
    bg.fill((10, 10, 20, 180))
    screen.blit(bg, (bx-4, by-4))

    if not flash:
        name_col = GOLD
    else:
        name_col = WHITE
    ns = font.render(f"Lv.{p.level}  Player", True, name_col)
    screen.blit(ns, (bx, by))

    _draw_bar(screen, bx, by+18, 180, 10, p.hp, p.max_hp, DARK_RED, (60,200,60))
    hp_t = font.render(f"HP {p.hp}/{p.max_hp}", True, WHITE)
    screen.blit(hp_t, (bx+184, by+16))

    _draw_bar(screen, bx, by+34, 180, 10, p.mp, p.max_mp, (20,20,100), (60,120,220))
    mp_t = font.render(f"MP {p.mp}/{p.max_mp}", True, WHITE)
    screen.blit(mp_t, (bx+184, by+32))


def _wrap_text(text, font, max_w):
    words  = text.split()
    lines  = []
    line   = ''
    for w in words:
        test = (line + ' ' + w).strip()
        if font.size(test)[0] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines
