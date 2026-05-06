import pygame
from .settings import (SCREEN_WIDTH, SCREEN_HEIGHT, TILESIZE,
                        BLACK, WHITE, RED, DARK_RED, GREEN, BLUE, YELLOW, GOLD,
                        DARK_GRAY, GRAY, LIGHT_GRAY, BROWN, PURPLE, CREAM,
                        ORANGE)


def draw_hud(screen, player, font_md, font_sm, current_map):
    p   = player
    pad = 10

    bg = pygame.Surface((220, 90), pygame.SRCALPHA)
    bg.fill((8, 6, 12, 200))
    screen.blit(bg, (pad - 4, pad - 4))

    name_surf = font_md.render(f"Lv.{p.level}  Hero", True, GOLD)
    screen.blit(name_surf, (pad, pad))

    _bar(screen, pad, pad+24, 180, 12, p.hp, p.max_hp, (140,20,20), (50,200,50))
    ht = font_sm.render(f"HP  {p.hp}/{p.max_hp}", True, WHITE)
    screen.blit(ht, (pad+184, pad+24))

    _bar(screen, pad, pad+42, 180, 12, p.mp, p.max_mp, (15,15,100), (40,100,220))
    mt = font_sm.render(f"MP  {p.mp}/{p.max_mp}", True, WHITE)
    screen.blit(mt, (pad+184, pad+42))

    exp_ratio  = 0
    from .settings import EXP_TABLE
    if p.level < len(EXP_TABLE) - 1:
        needed = EXP_TABLE[p.level] - EXP_TABLE[p.level-1]
        done   = p.exp - EXP_TABLE[p.level-1]
        exp_ratio = max(0, min(1, done / needed)) if needed else 1
    _bar(screen, pad, pad+60, 180, 8, int(exp_ratio*100), 100, (40,30,60), (160,60,220))
    et = font_sm.render(f"EXP  {p.exp_to_next()} to next", True, (180,140,220))
    screen.blit(et, (pad+184, pad+58))

    map_names = {'village': 'Village', 'forest': 'Haunted Forest', 'dungeon': 'Dark Dungeon'}
    mn = font_sm.render(map_names.get(current_map, current_map), True, (160,200,160))
    screen.blit(mn, (SCREEN_WIDTH - mn.get_width() - 10, 10))

    ctrl = font_sm.render("WASD/Arrows:Move  E:Talk  ESC:Quit", True, (100,100,100))
    screen.blit(ctrl, (SCREEN_WIDTH//2 - ctrl.get_width()//2, SCREEN_HEIGHT - 18))


def _bar(screen, x, y, w, h, val, maxval, bg, fg):
    pygame.draw.rect(screen, bg, (x, y, w, h), border_radius=4)
    filled = int(w * val / maxval) if maxval > 0 else 0
    if filled:
        pygame.draw.rect(screen, fg, (x, y, filled, h), border_radius=4)
    pygame.draw.rect(screen, (80, 80, 80), (x, y, w, h), border_radius=4, width=1)


class DialogBox:
    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg  = font_lg
        self.font_md  = font_md
        self.font_sm  = font_sm
        self.active   = False
        self.lines    = []
        self.speaker  = ''
        self.page     = 0
        self.reveal   = 0.0
        self.speed    = 30

    def open(self, speaker, lines):
        self.speaker = speaker
        self.lines   = lines
        self.page    = 0
        self.reveal  = 0.0
        self.active  = True

    def update(self, dt):
        if not self.active:
            return
        self.reveal = min(len(self.lines[self.page]), self.reveal + self.speed * dt)

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE,
                                                           pygame.K_z, pygame.K_e):
            if self.reveal < len(self.lines[self.page]):
                self.reveal = len(self.lines[self.page])
            else:
                self.page += 1
                if self.page >= len(self.lines):
                    self.active = False
                else:
                    self.reveal = 0.0
            return True
        return False

    def draw(self, screen):
        if not self.active:
            return
        bw = SCREEN_WIDTH - 60
        bh = 120
        bx = 30
        by = SCREEN_HEIGHT - bh - 20

        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((12, 10, 20, 220))
        screen.blit(bg, (bx, by))
        pygame.draw.rect(screen, GOLD,  (bx, by, bw, bh), border_radius=6, width=2)

        sp = self.font_md.render(self.speaker, True, GOLD)
        screen.blit(sp, (bx+12, by+8))

        if self.page < len(self.lines):
            text  = self.lines[self.page][:int(self.reveal)]
            words = text.split()
            line  = ''
            lines = []
            for w in words:
                test = (line + ' ' + w).strip()
                if self.font_sm.size(test)[0] <= bw - 24:
                    line = test
                else:
                    lines.append(line)
                    line = w
            if line:
                lines.append(line)

            for i, l in enumerate(lines[:3]):
                s = self.font_sm.render(l, True, CREAM)
                screen.blit(s, (bx+12, by+34+i*24))

        if self.reveal >= len(self.lines[self.page] if self.page < len(self.lines) else ''):
            arrow_x = bx + bw - 24
            arrow_y = by + bh - 20
            col     = GOLD if (pygame.time.get_ticks() // 400) % 2 == 0 else (180, 140, 0)
            pygame.draw.polygon(screen, col, [
                (arrow_x, arrow_y), (arrow_x+10, arrow_y), (arrow_x+5, arrow_y+8)])


class LevelUpScreen:
    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg = font_lg
        self.font_md = font_md
        self.font_sm = font_sm
        self.active  = False
        self.timer   = 0.0
        self.level   = 1

    def show(self, level):
        self.active = True
        self.timer  = 3.5
        self.level  = level

    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False

    def draw(self, screen):
        if not self.active:
            return
        alpha = min(255, int(255 * min(1.0, self.timer / 3.5 * 2)))
        panel = pygame.Surface((400, 100), pygame.SRCALPHA)
        panel.fill((20, 15, 40, 200))
        screen.blit(panel, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))

        t1 = self.font_lg.render("LEVEL UP!", True, GOLD)
        t2 = self.font_md.render(f"You are now Level {self.level}!", True, WHITE)
        t3 = self.font_sm.render("All stats increased!", True, (180, 140, 220))
        screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, SCREEN_HEIGHT//2 - 46))
        screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, SCREEN_HEIGHT//2 - 6))
        screen.blit(t3, (SCREEN_WIDTH//2 - t3.get_width()//2, SCREEN_HEIGHT//2 + 26))


class GameOverScreen:
    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg = font_lg
        self.font_md = font_md
        self.font_sm = font_sm

    def draw(self, screen):
        screen.fill((5, 0, 8))
        t1 = self.font_lg.render("YOU DIED", True, RED)
        t2 = self.font_md.render("Press ENTER to try again", True, LIGHT_GRAY)
        t3 = self.font_sm.render("The darkness claims another soul...", True, GRAY)
        screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, SCREEN_HEIGHT//2 - 60))
        screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(t3, (SCREEN_WIDTH//2 - t3.get_width()//2, SCREEN_HEIGHT//2 + 40))


class WinScreen:
    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg = font_lg
        self.font_md = font_md
        self.font_sm = font_sm

    def draw(self, screen, player):
        screen.fill((5, 2, 15))
        stars = [(i*97 % SCREEN_WIDTH, i*83 % SCREEN_HEIGHT) for i in range(80)]
        for sx, sy in stars:
            pygame.draw.circle(screen, WHITE, (sx, sy), 1)

        t1 = self.font_lg.render("VICTORY!", True, GOLD)
        t2 = self.font_md.render("The Dark Lord has been vanquished!", True, WHITE)
        t3 = self.font_md.render(f"Final Level: {player.level}   EXP: {player.exp}", True, (180,220,180))
        t4 = self.font_sm.render("Press ENTER to play again", True, LIGHT_GRAY)
        screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, SCREEN_HEIGHT//2 - 80))
        screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, SCREEN_HEIGHT//2 - 20))
        screen.blit(t3, (SCREEN_WIDTH//2 - t3.get_width()//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(t4, (SCREEN_WIDTH//2 - t4.get_width()//2, SCREEN_HEIGHT//2 + 60))


class TitleScreen:
    def __init__(self, font_lg, font_md, font_sm):
        self.font_lg = font_lg
        self.font_md = font_md
        self.font_sm = font_sm
        self.tick    = 0.0

    def update(self, dt):
        self.tick += dt

    def draw(self, screen):
        screen.fill((8, 5, 18))
        stars = [(i*97 % SCREEN_WIDTH, i*83 % SCREEN_HEIGHT) for i in range(100)]
        for sx, sy in stars:
            r = 1 if (sx + sy) % 3 == 0 else 0
            pygame.draw.circle(screen, WHITE, (sx, sy), r+1)

        blink = (int(self.tick * 2) % 2 == 0)
        t1 = self.font_lg.render("PyRPG", True, GOLD)
        t2 = self.font_md.render("Adventure Begins", True, (180, 160, 220))
        t3 = self.font_sm.render("Defeat the Dark Lord and save the kingdom", True, (140, 180, 140))
        t4 = self.font_md.render("Press ENTER to start", True, WHITE if blink else GRAY)
        t5 = self.font_sm.render("WASD / Arrow Keys to move   E to talk   ESC to quit", True, (100, 100, 130))

        screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, SCREEN_HEIGHT//2 - 110))
        screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(t3, (SCREEN_WIDTH//2 - t3.get_width()//2, SCREEN_HEIGHT//2 - 10))
        screen.blit(t4, (SCREEN_WIDTH//2 - t4.get_width()//2, SCREEN_HEIGHT//2 + 40))
        screen.blit(t5, (SCREEN_WIDTH//2 - t5.get_width()//2, SCREEN_HEIGHT//2 + 80))
