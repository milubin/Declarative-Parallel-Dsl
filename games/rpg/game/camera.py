import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILESIZE


class Camera:
    def __init__(self, map_w, map_h):
        self.offset = pygame.math.Vector2(0, 0)
        self.map_w  = map_w * TILESIZE
        self.map_h  = map_h * TILESIZE

    def apply(self, rect):
        return rect.move(-int(self.offset.x), -int(self.offset.y))

    def apply_vec(self, vec):
        return pygame.math.Vector2(vec.x - self.offset.x, vec.y - self.offset.y)

    def update(self, target_rect):
        cx = target_rect.centerx - SCREEN_WIDTH  // 2
        cy = target_rect.centery - SCREEN_HEIGHT // 2
        cx = max(0, min(cx, self.map_w - SCREEN_WIDTH))
        cy = max(0, min(cy, self.map_h - SCREEN_HEIGHT))
        self.offset = pygame.math.Vector2(cx, cy)
