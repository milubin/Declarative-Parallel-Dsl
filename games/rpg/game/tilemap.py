import pygame
from .settings import TILESIZE, TILE_COLOR, TILE_SOLID, SCREEN_WIDTH, SCREEN_HEIGHT


def _draw_grass_tile(surf, rect):
    pygame.draw.rect(surf, TILE_COLOR['.'], rect)
    for ox, oy in [(4, 8), (14, 5), (22, 12), (8, 20), (26, 18)]:
        if rect.x % 64 == 0 or rect.y % 96 == 0:
            col = (70, 140, 55)
            pygame.draw.line(surf, col, (rect.x+ox, rect.y+oy), (rect.x+ox, rect.y+oy-5), 2)


def _draw_tree_tile(surf, rect):
    pygame.draw.rect(surf, (25, 65, 25), rect)
    cx, cy = rect.centerx, rect.centery
    pygame.draw.polygon(surf, (40, 100, 40), [
        (cx, rect.y+2), (rect.x+4, rect.bottom-6), (rect.right-4, rect.bottom-6)
    ])
    pygame.draw.rect(surf, (90, 55, 25), (cx-3, rect.bottom-8, 6, 8))


def _draw_water_tile(surf, rect, tick):
    base = TILE_COLOR['~']
    pygame.draw.rect(surf, base, rect)
    wave_y = rect.y + 10 + (tick // 30 % 4)
    pygame.draw.line(surf, (80, 140, 220), (rect.x+2, wave_y), (rect.x+14, wave_y), 2)
    pygame.draw.line(surf, (80, 140, 220), (rect.x+16, wave_y+6), (rect.right-2, wave_y+6), 2)


def _draw_wall_tile(surf, rect):
    pygame.draw.rect(surf, TILE_COLOR['W'], rect)
    for row in range(2):
        for col in range(2):
            bx = rect.x + col*16
            by = rect.y + row*16
            pygame.draw.rect(surf, (70, 65, 60), (bx+1, by+1, 14, 14))
            pygame.draw.rect(surf, (110, 105, 100), (bx+1, by+1, 14, 14), 1)


def _draw_path_tile(surf, rect):
    pygame.draw.rect(surf, TILE_COLOR['P'], rect)
    pygame.draw.rect(surf, (130, 105, 65), rect, 1)


def _draw_floor_tile(surf, rect):
    pygame.draw.rect(surf, TILE_COLOR['F'], rect)
    pygame.draw.rect(surf, (155, 128, 80), rect, 1)


def _draw_dungeon_floor(surf, rect):
    pygame.draw.rect(surf, TILE_COLOR['G'], rect)
    pygame.draw.rect(surf, (45, 40, 35), rect, 1)


def _draw_dungeon_wall(surf, rect):
    pygame.draw.rect(surf, TILE_COLOR['B'], rect)
    pygame.draw.rect(surf, (55, 48, 40), rect, 1)


def _draw_door_tile(surf, rect):
    pygame.draw.rect(surf, TILE_COLOR['D'], rect)
    pygame.draw.rect(surf, (80, 45, 10), (rect.x+6, rect.y+4, 20, 24))
    pygame.draw.circle(surf, (200, 170, 60), (rect.x+22, rect.centery), 3)


def _draw_sand_tile(surf, rect):
    pygame.draw.rect(surf, TILE_COLOR['S'], rect)


def _draw_shrub_tile(surf, rect):
    pygame.draw.rect(surf, (60, 100, 45), rect)
    pygame.draw.circle(surf, (50, 130, 50), rect.center, 10)


TILE_RENDERERS = {
    '.': _draw_grass_tile,
    '#': _draw_tree_tile,
    '~': _draw_water_tile,
    'W': _draw_wall_tile,
    'D': _draw_door_tile,
    'P': _draw_path_tile,
    'F': _draw_floor_tile,
    'G': _draw_dungeon_floor,
    'B': _draw_dungeon_wall,
    'S': _draw_sand_tile,
    '_': _draw_floor_tile,
    '^': _draw_shrub_tile,
    'T': _draw_tree_tile,
}


class TileMap:
    def __init__(self, map_data):
        self.data   = map_data
        self.rows   = len(map_data)
        self.cols   = max(len(row) for row in map_data)
        self._cache = None
        self._tick  = 0

    def _build_cache(self):
        w = self.cols * TILESIZE
        h = self.rows * TILESIZE
        surf = pygame.Surface((w, h))
        for r, row in enumerate(self.data):
            for c, ch in enumerate(row):
                rect = pygame.Rect(c * TILESIZE, r * TILESIZE, TILESIZE, TILESIZE)
                renderer = TILE_RENDERERS.get(ch)
                if renderer:
                    if ch == '~':
                        renderer(surf, rect, self._tick)
                    else:
                        renderer(surf, rect)
                else:
                    pygame.draw.rect(surf, (50, 50, 50), rect)
        self._cache = surf

    def draw(self, screen, camera, tick):
        if self._cache is None or tick % 60 == 0:
            self._tick = tick
            self._build_cache()
        screen.blit(self._cache, (-int(camera.offset.x), -int(camera.offset.y)))

    def is_solid(self, grid_x, grid_y):
        if grid_y < 0 or grid_y >= self.rows:
            return True
        if grid_x < 0 or grid_x >= self.cols:
            return True
        row = self.data[grid_y]
        if grid_x >= len(row):
            return True
        ch = row[grid_x]
        return TILE_SOLID.get(ch, True)

    def tile_at(self, grid_x, grid_y):
        if 0 <= grid_y < self.rows and 0 <= grid_x < len(self.data[grid_y]):
            return self.data[grid_y][grid_x]
        return 'B'

    def pixel_rect_solid(self, rect):
        margin = 2
        left   = (rect.left   + margin) // TILESIZE
        right  = (rect.right  - margin) // TILESIZE
        top    = (rect.top    + margin) // TILESIZE
        bottom = (rect.bottom - margin) // TILESIZE
        for gy in range(top, bottom+1):
            for gx in range(left, right+1):
                if self.is_solid(gx, gy):
                    return True
        return False
