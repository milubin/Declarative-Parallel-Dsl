SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
TITLE = "PyRPG — Adventure Begins"
FPS = 60

TILESIZE = 32

BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
RED         = (220, 50,  50)
DARK_RED    = (140, 20,  20)
GREEN       = (60,  180, 60)
DARK_GREEN  = (30,  90,  30)
BLUE        = (50,  100, 220)
YELLOW      = (240, 200, 50)
GOLD        = (255, 215, 0)
DARK_GRAY   = (35,  35,  35)
GRAY        = (100, 100, 100)
LIGHT_GRAY  = (180, 180, 180)
BROWN       = (120, 75,  35)
DARK_BROWN  = (70,  40,  15)
ORANGE      = (230, 130, 30)
PURPLE      = (140, 50,  180)
TEAL        = (30,  160, 140)
PINK        = (220, 100, 140)
CREAM       = (240, 220, 170)

TILE_COLOR = {
    '.': (86,  155, 67),
    '#': (34,  85,  34),
    '~': (50,  110, 200),
    'W': (90,  85,  80),
    'D': (110, 70,  30),
    'P': (150, 125, 85),
    'F': (175, 148, 100),
    'G': (55,  50,  45),
    'B': (38,  33,  28),
    'S': (205, 185, 125),
    'T': (38,  85,  38),
    '_': (130, 115, 80),
    '^': (90,  130, 90),
}

TILE_SOLID = {
    '.': False, '#': True,  '~': True,  'W': True,
    'D': False, 'P': False, 'F': False, 'G': False,
    'B': True,  'S': False, 'T': True,  '_': False,
    '^': False,
}

PLAYER_SPEED  = 160
PLAYER_HP     = 100
PLAYER_MP     = 60
PLAYER_ATK    = 12
PLAYER_DEF    = 5
PLAYER_MAGIC  = 10

DIR_DOWN  = 0
DIR_LEFT  = 1
DIR_RIGHT = 2
DIR_UP    = 3

STATE_EXPLORE = 'explore'
STATE_BATTLE  = 'battle'
STATE_DIALOG  = 'dialog'
STATE_GAMEOVER = 'gameover'
STATE_WIN      = 'win'
STATE_LEVELUP  = 'levelup'

EXP_TABLE = [0, 20, 50, 95, 155, 235, 340, 475, 645, 860, 1120]
