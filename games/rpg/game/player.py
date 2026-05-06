import pygame
from .settings import (TILESIZE, PLAYER_SPEED, PLAYER_HP, PLAYER_MP,
                        PLAYER_ATK, PLAYER_DEF, PLAYER_MAGIC,
                        DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_UP, EXP_TABLE,
                        WHITE, YELLOW, BLUE, RED, DARK_GRAY, GOLD, GREEN)


def draw_player_sprite(surf, rect, direction, frame):
    cx, cy = rect.centerx, rect.centery
    ts = TILESIZE

    body_col  = (60, 100, 200)
    skin_col  = (240, 195, 145)
    hair_col  = (90,  60,  20)
    boot_col  = (50,  35,  15)

    pygame.draw.rect(surf, boot_col,  (rect.x+4,  rect.y+22, 8,  10))
    pygame.draw.rect(surf, boot_col,  (rect.x+18, rect.y+22, 8,  10))

    pygame.draw.rect(surf, body_col,  (rect.x+5,  rect.y+14, 22, 12))

    head_rect = pygame.Rect(rect.x+8, rect.y+2, 16, 14)
    pygame.draw.rect(surf, skin_col, head_rect, border_radius=4)
    pygame.draw.rect(surf, hair_col, (rect.x+8, rect.y+2, 16, 6), border_radius=4)

    if direction == DIR_DOWN:
        pygame.draw.circle(surf, (20, 20, 20), (rect.x+13, rect.y+10), 2)
        pygame.draw.circle(surf, (20, 20, 20), (rect.x+19, rect.y+10), 2)
        pygame.draw.line(surf, (180, 120, 90), (rect.x+14, rect.y+13), (rect.x+18, rect.y+13), 1)
    elif direction == DIR_UP:
        pass
    elif direction == DIR_LEFT:
        pygame.draw.circle(surf, (20, 20, 20), (rect.x+12, rect.y+10), 2)
        pygame.draw.line(surf, (180, 120, 90), (rect.x+11, rect.y+13), (rect.x+16, rect.y+13), 1)
    elif direction == DIR_RIGHT:
        pygame.draw.circle(surf, (20, 20, 20), (rect.x+18, rect.y+10), 2)
        pygame.draw.line(surf, (180, 120, 90), (rect.x+16, rect.y+13), (rect.x+21, rect.y+13), 1)

    sword_col = (200, 200, 220)
    if direction == DIR_RIGHT:
        arm_x = rect.right - 4
        sway  = 2 if frame % 2 == 0 else -2
        pygame.draw.line(surf, sword_col, (arm_x, rect.y+16+sway), (arm_x+10, rect.y+8+sway), 2)
    elif direction == DIR_LEFT:
        arm_x = rect.x + 4
        sway  = 2 if frame % 2 == 0 else -2
        pygame.draw.line(surf, sword_col, (arm_x, rect.y+16+sway), (arm_x-10, rect.y+8+sway), 2)
    elif direction == DIR_UP:
        sway = 2 if frame % 2 == 0 else -2
        pygame.draw.line(surf, sword_col, (rect.x+8+sway, rect.y+16), (rect.x+4+sway, rect.y+4), 2)
    else:
        sway = 2 if frame % 2 == 0 else -2
        pygame.draw.line(surf, sword_col, (rect.right-8+sway, rect.y+14), (rect.right+2+sway, rect.y+24), 2)


class Player:
    def __init__(self, grid_x, grid_y):
        self.size      = TILESIZE
        self.rect      = pygame.Rect(grid_x * TILESIZE, grid_y * TILESIZE, self.size, self.size)
        self.pos       = pygame.math.Vector2(self.rect.topleft)
        self.direction = DIR_DOWN
        self.moving    = False
        self.frame     = 0
        self.anim_tick = 0

        self.level    = 1
        self.exp      = 0
        self.max_hp   = PLAYER_HP
        self.hp       = PLAYER_HP
        self.max_mp   = PLAYER_MP
        self.mp       = PLAYER_MP
        self.atk      = PLAYER_ATK
        self.defense  = PLAYER_DEF
        self.magic    = PLAYER_MAGIC

        self.invincible      = False
        self.invincible_timer = 0
        self.flash           = False

    def handle_input(self, keys, tilemap, dt):
        dx, dy    = 0, 0
        self.moving = False

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            dx = -1; self.direction = DIR_LEFT;  self.moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx =  1; self.direction = DIR_RIGHT; self.moving = True
        elif keys[pygame.K_UP]   or keys[pygame.K_w]:
            dy = -1; self.direction = DIR_UP;    self.moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy =  1; self.direction = DIR_DOWN;  self.moving = True

        speed = PLAYER_SPEED * dt

        if dx != 0:
            new_pos = self.pos + pygame.math.Vector2(dx * speed, 0)
            test    = pygame.Rect(int(new_pos.x), int(self.pos.y), self.size, self.size)
            if not tilemap.pixel_rect_solid(test):
                self.pos.x = new_pos.x
        if dy != 0:
            new_pos = self.pos + pygame.math.Vector2(0, dy * speed)
            test    = pygame.Rect(int(self.pos.x), int(new_pos.y), self.size, self.size)
            if not tilemap.pixel_rect_solid(test):
                self.pos.y = new_pos.y

        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def update(self, dt):
        if self.invincible:
            self.invincible_timer -= dt
            self.flash = int(self.invincible_timer * 10) % 2 == 0
            if self.invincible_timer <= 0:
                self.invincible = False
                self.flash      = False

        if self.moving:
            self.anim_tick += 1
            if self.anim_tick >= 8:
                self.anim_tick = 0
                self.frame     = (self.frame + 1) % 4
        else:
            self.frame = 0

    def draw(self, screen, camera):
        draw_rect = camera.apply(self.rect)
        if not self.flash:
            draw_player_sprite(screen, draw_rect, self.direction, self.frame)
        shadow = pygame.Surface((self.size, 6), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 60))
        screen.blit(shadow, (draw_rect.x + 4, draw_rect.bottom - 4))

    def take_damage(self, amount):
        if self.invincible:
            return
        dmg = max(1, amount - self.defense)
        self.hp = max(0, self.hp - dmg)
        self.invincible       = True
        self.invincible_timer = 1.5
        return dmg

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def restore_mp(self, amount):
        self.mp = min(self.max_mp, self.mp + amount)

    def gain_exp(self, amount):
        self.exp += amount
        leveled = False
        while self.level < len(EXP_TABLE) - 1 and self.exp >= EXP_TABLE[self.level]:
            self.level += 1
            self.max_hp   += 20
            self.hp        = self.max_hp
            self.max_mp   += 10
            self.mp        = self.max_mp
            self.atk      += 4
            self.defense  += 2
            self.magic    += 3
            leveled = True
        return leveled

    def exp_to_next(self):
        if self.level >= len(EXP_TABLE) - 1:
            return 0
        return EXP_TABLE[self.level] - self.exp

    def grid_pos(self):
        return self.rect.centerx // TILESIZE, self.rect.centery // TILESIZE

    def set_grid_pos(self, gx, gy):
        self.rect.x = gx * TILESIZE
        self.rect.y = gy * TILESIZE
        self.pos    = pygame.math.Vector2(self.rect.topleft)
