import pygame
import random
from .settings import TILESIZE, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_UP, WHITE


def draw_npc_sprite(surf, rect, color, frame, direction):
    cx = rect.centerx
    pygame.draw.rect(surf, (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)),
                     (rect.x+5, rect.y+18, 22, 12))
    head = pygame.Rect(rect.x+7, rect.y+3, 18, 15)
    pygame.draw.rect(surf, color, head, border_radius=5)
    pygame.draw.rect(surf, (max(0,color[0]-40), max(0,color[1]-40), max(0,color[2]-40)),
                     (rect.x+6, rect.y+2, 20, 8), border_radius=5)
    if direction == DIR_DOWN:
        pygame.draw.circle(surf, (20,20,20), (rect.x+12, rect.y+11), 2)
        pygame.draw.circle(surf, (20,20,20), (rect.x+20, rect.y+11), 2)

    bob = 1 if frame % 2 == 0 else 0
    pygame.draw.rect(surf, (60,45,25), (rect.x+7, rect.y+28+bob, 8, 5))
    pygame.draw.rect(surf, (60,45,25), (rect.x+17, rect.y+28+bob, 8, 5))


def draw_enemy_sprite(surf, rect, etype, frame, hp_ratio):
    if etype == 'slime':
        col = (70, 200, 100)
        bob = 2 if frame % 2 == 0 else 0
        pygame.draw.ellipse(surf, col, (rect.x+4, rect.y+12+bob, 24, 18))
        pygame.draw.ellipse(surf, (50,160,80), (rect.x+4, rect.y+12+bob, 24, 18), 2)
        pygame.draw.circle(surf, (20,20,20), (rect.x+12, rect.y+17+bob), 3)
        pygame.draw.circle(surf, (20,20,20), (rect.x+20, rect.y+17+bob), 3)
        pygame.draw.ellipse(surf, (120,230,150), (rect.x+6, rect.y+14+bob, 8, 5))
    elif etype == 'wolf':
        col = (130,100,75)
        bob = 1 if frame % 2 == 0 else -1
        pygame.draw.ellipse(surf, col, (rect.x+4, rect.y+10+bob, 24, 16))
        pygame.draw.ellipse(surf, col, (rect.x+10, rect.y+4+bob, 14, 14))
        pygame.draw.polygon(surf, col, [
            (rect.x+10, rect.y+4+bob), (rect.x+8,  rect.y+bob),    (rect.x+13, rect.y+5+bob)])
        pygame.draw.polygon(surf, col, [
            (rect.x+20, rect.y+4+bob), (rect.x+24, rect.y+bob),    (rect.x+19, rect.y+5+bob)])
        pygame.draw.circle(surf, (220,200,60), (rect.x+14, rect.y+9+bob), 2)
        pygame.draw.circle(surf, (220,200,60), (rect.x+19, rect.y+9+bob), 2)
        pygame.draw.circle(surf, (20,20,20), (rect.x+14, rect.y+9+bob), 1)
        pygame.draw.circle(surf, (20,20,20), (rect.x+19, rect.y+9+bob), 1)
    elif etype == 'skeleton':
        bob = 1 if frame % 2 == 0 else -1
        pygame.draw.circle(surf, (215,210,195), (rect.centerx, rect.y+10+bob), 10)
        pygame.draw.rect(surf,   (215,210,195), (rect.x+10, rect.y+18+bob, 12, 10))
        for bx in [rect.x+11, rect.x+17]:
            pygame.draw.rect(surf, (215,210,195), (bx, rect.y+28+bob, 4, 8))
        pygame.draw.circle(surf, (20,20,20), (rect.x+14, rect.y+9+bob), 2)
        pygame.draw.circle(surf, (20,20,20), (rect.x+19, rect.y+9+bob), 2)
    elif etype == 'zombie':
        col = (100,155,80)
        bob = 1 if frame % 4 < 2 else -1
        pygame.draw.rect(surf, col, (rect.x+8, rect.y+14+bob, 16, 16))
        pygame.draw.circle(surf, (130,180,100), (rect.centerx, rect.y+9+bob), 10)
        pygame.draw.circle(surf, (20,20,20), (rect.x+14, rect.y+8+bob), 2)
        pygame.draw.circle(surf, (20,20,20), (rect.x+19, rect.y+8+bob), 2)
        pygame.draw.line(surf, col, (rect.x+5, rect.y+18+bob), (rect.x+0, rect.y+14+bob), 3)
        pygame.draw.line(surf, col, (rect.right-5, rect.y+18+bob), (rect.right, rect.y+14+bob), 3)
    elif etype == 'boss':
        bob = 2 if frame % 2 == 0 else 0
        col = (140,20,160)
        pygame.draw.rect(surf, col, (rect.x+2, rect.y+10+bob, 28, 20))
        pygame.draw.circle(surf, (180,30,200), (rect.centerx, rect.y+8+bob), 13)
        pygame.draw.polygon(surf, (220,180,0), [
            (rect.x+6, rect.y+8+bob), (rect.x+2, rect.y-2+bob), (rect.x+10, rect.y+4+bob)])
        pygame.draw.polygon(surf, (220,180,0), [
            (rect.right-6, rect.y+8+bob), (rect.right-2, rect.y-2+bob), (rect.right-10, rect.y+4+bob)])
        pygame.draw.circle(surf, (255,50,50), (rect.x+14, rect.y+7+bob), 3)
        pygame.draw.circle(surf, (255,50,50), (rect.x+20, rect.y+7+bob), 3)
        for i in range(4):
            mx = rect.x + 4 + i*7
            pygame.draw.rect(surf, (100,10,120), (mx, rect.y+28+bob, 5, 5))

    bar_w = int(TILESIZE * hp_ratio)
    pygame.draw.rect(surf, (180,30,30), (rect.x, rect.y-6, TILESIZE, 4))
    pygame.draw.rect(surf, (60,200,60), (rect.x, rect.y-6, bar_w, 4))


class NPC:
    def __init__(self, grid_x, grid_y, name, color, dialog):
        self.rect      = pygame.Rect(grid_x * TILESIZE, grid_y * TILESIZE, TILESIZE, TILESIZE)
        self.name      = name
        self.color     = color
        self.dialog    = dialog
        self.direction = DIR_DOWN
        self.frame     = 0
        self.tick      = 0
        self.wander_timer = random.uniform(1, 3)
        self.dx = 0; self.dy = 0

    def update(self, dt, tilemap):
        self.tick += dt
        if self.tick >= self.wander_timer:
            self.tick = 0
            self.wander_timer = random.uniform(1.5, 4)
            choices = [(1,0),(-1,0),(0,1),(0,-1),(0,0),(0,0)]
            self.dx, self.dy = random.choice(choices)
            if   self.dx  >  0: self.direction = DIR_RIGHT
            elif self.dx  <  0: self.direction = DIR_LEFT
            elif self.dy  >  0: self.direction = DIR_DOWN
            elif self.dy  <  0: self.direction = DIR_UP

        speed = 40
        nx = self.rect.x + self.dx * speed * dt
        ny = self.rect.y + self.dy * speed * dt
        test_x = pygame.Rect(int(nx), self.rect.y, TILESIZE, TILESIZE)
        test_y = pygame.Rect(self.rect.x, int(ny), TILESIZE, TILESIZE)
        if not tilemap.pixel_rect_solid(test_x):
            self.rect.x = int(nx)
        if not tilemap.pixel_rect_solid(test_y):
            self.rect.y = int(ny)

        self.frame = int(self.tick * 4) % 4

    def draw(self, screen, camera):
        r = camera.apply(self.rect)
        draw_npc_sprite(screen, r, self.color, self.frame, self.direction)

    def is_adjacent(self, player_rect):
        expanded = self.rect.inflate(TILESIZE * 2, TILESIZE * 2)
        return expanded.colliderect(player_rect)


class Enemy:
    def __init__(self, grid_x, grid_y, etype, stats):
        self.rect      = pygame.Rect(grid_x * TILESIZE, grid_y * TILESIZE, TILESIZE, TILESIZE)
        self.etype     = etype
        self.name      = stats['name']
        self.max_hp    = stats['hp']
        self.hp        = stats['hp']
        self.atk       = stats['atk']
        self.defense   = stats['def']
        self.exp_reward= stats['exp']
        self.color     = stats['color']
        self.is_boss   = etype == 'boss'
        self.frame     = 0
        self.tick      = 0
        self.alive     = True

    def update(self, dt, tilemap, player_rect):
        self.tick += dt
        self.frame = int(self.tick * 6) % 4

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = (dx**2 + dy**2) ** 0.5
        aggro_range = TILESIZE * (8 if self.is_boss else 5)

        if dist < aggro_range and dist > 0:
            speed = 55 * dt
            nx = self.rect.x + (dx / dist) * speed
            ny = self.rect.y + (dy / dist) * speed
            test_x = pygame.Rect(int(nx), self.rect.y, TILESIZE, TILESIZE)
            test_y = pygame.Rect(self.rect.x, int(ny), TILESIZE, TILESIZE)
            if not tilemap.pixel_rect_solid(test_x):
                self.rect.x = int(nx)
            if not tilemap.pixel_rect_solid(test_y):
                self.rect.y = int(ny)

    def draw(self, screen, camera):
        if not self.alive:
            return
        r = camera.apply(self.rect)
        draw_enemy_sprite(screen, r, self.etype, self.frame, self.hp / self.max_hp)

    def hp_ratio(self):
        return self.hp / self.max_hp
