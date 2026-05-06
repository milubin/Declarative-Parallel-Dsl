VILLAGE = [
    "##############################",
    "#............................#",
    "#............................#",
    "#....PP......................#",
    "#....PP....WWWW..WWWW........#",
    "#....PP....W__W..W__W........#",
    "#....PP....W__D..D__W........#",
    "#....PPPPPPPPPPPPPPPP........#",
    "#............PP..............#",
    "#............PP..............#",
    "#............PP..............#",
    "#............PP..............#",
    "#....WWWW....PP..............#",
    "#....W__W....PP..............#",
    "#....D__W....PP..............#",
    "#....WWWW....PP..............#",
    "#............PP..............#",
    "#...........PPP...............",
    "#...........P.................",
    "##############################",
]

FOREST = [
    "##############################",
    "#^^^^#...#^^^....#^^^^^^^....#",
    "#^...#...#.......#^..........#",
    "#^...........^...............#",
    "#^.....SS....^.....^^........#",
    "#......SS..............^^....#",
    "#............^.......^^^.....#",
    ".......^.....^.......^.......#",
    "......^^^^^.................##",
    "..........^.......PP.........#",
    "..........^.......PP.........#",
    "..........^.......PP.........#",
    "#.........^......#PP.........#",
    "#^.......^.......#PP.........#",
    "#^.......^........PP.........#",
    "#^^......^^.......PP.........#",
    "#^...............^PP.........#",
    "#^^..............PPP.........#",
    "#.............PPPP...........#",
    "##############################",
]

DUNGEON = [
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    "BGGGGGBBBBBBBBBBBBBBBBBBBBGGGB",
    "BGGGBBBBBBBBBBGGGGGBBBBBBGGGBB",
    "BGGGBGGGGGGGGGGGGGGGBBBBBGGGBB",
    "BGGGBGBBBBBBBBBBGGGGGBBBGGGGBB",
    "BGGGGGBGGGGGGGGGGGGGGBBGGGGBBB",
    "BGGBBBGGGGBBBBBBGGGGGBBGGGBBBB",
    "BGGBGGGGGGBBBBBBGGGGGBBGGGBBBB",
    "BGGBGGGGGGBBGGGGGGGGGBBGGGBBBB",
    "BGGBGGGGGGBBGBBBGBBBGBBGGGBBBB",
    "BGGBGGGGGGGGGBBBGBBBGBGGGBBBB",
    "BGGBGGBBBBBBGBBGGGBGGGGGGBBBB",
    "BGGGGGGBBBBBBBBGGGGGGGGGBBBBB",
    "BBBBBBGGGGGGGGGGGGGGGGGBBBBBB",
    "BBBBBGGGGGGGGGGGGGGGGGGGBBBBB",
    "BBBBGGGGBBBBBBBBBBBGGGGGGBBBB",
    "BBBGGGGGBGGGGGGGGGBGGGGGBBBBB",
    "BBGGGBBBBBGGGGGGGBBBBBBGBBBBB",
    "BGGGBBBBBBGGGGGGGBBBBBBGBBGBB",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
]

NPC_DATA = {
    'village': [
        {'x': 4,  'y': 3,  'name': 'Elder',    'color': (200, 160, 100),
         'dialog': ["Welcome, brave adventurer!", "Our village is threatened by monsters.", "Head east into the forest — be careful!"]},
        {'x': 10, 'y': 13, 'name': 'Merchant', 'color': (180, 120, 60),
         'dialog': ["I sell potions and gear.", "The forest east of here is dangerous.", "I hear a dungeon lies beyond the forest..."]},
        {'x': 17, 'y': 5,  'name': 'Villager', 'color': (150, 180, 150),
         'dialog': ["Don't go into the forest alone!", "Monsters have been appearing at night."]},
        {'x': 6,  'y': 14, 'name': 'Smith',    'color': (130, 130, 160),
         'dialog': ["I forge the finest blades.", "Return when you've gained some experience.", "A legendary sword awaits a true hero!"]},
    ],
    'forest': [],
    'dungeon': [],
}

ENEMY_DATA = {
    'village': [],
    'forest': [
        {'x': 5,  'y': 2,  'type': 'slime'},
        {'x': 12, 'y': 5,  'type': 'slime'},
        {'x': 3,  'y': 8,  'type': 'wolf'},
        {'x': 18, 'y': 3,  'type': 'wolf'},
        {'x': 8,  'y': 14, 'type': 'slime'},
        {'x': 15, 'y': 13, 'type': 'wolf'},
        {'x': 25, 'y': 7,  'type': 'wolf'},
    ],
    'dungeon': [
        {'x': 3,  'y': 3,  'type': 'skeleton'},
        {'x': 10, 'y': 5,  'type': 'skeleton'},
        {'x': 5,  'y': 10, 'type': 'zombie'},
        {'x': 15, 'y': 8,  'type': 'skeleton'},
        {'x': 20, 'y': 3,  'type': 'zombie'},
        {'x': 7,  'y': 16, 'type': 'zombie'},
        {'x': 14, 'y': 14, 'type': 'boss',  'boss': True},
    ],
}

TRANSITIONS = {
    'village': [
        {'from_tiles': [(28, 17), (28, 18)], 'to_map': 'forest', 'spawn': (1, 9)},
    ],
    'forest': [
        {'from_tiles': [(0, 7), (0, 8)],  'to_map': 'village', 'spawn': (27, 17)},
        {'from_tiles': [(28, 9), (28, 10), (28, 11)], 'to_map': 'dungeon', 'spawn': (1, 18)},
    ],
    'dungeon': [
        {'from_tiles': [(1, 18), (1, 17)], 'to_map': 'forest',  'spawn': (27, 10)},
    ],
}

SPAWN_POS = {
    'village':  (5, 8),
    'forest':   (1, 9),
    'dungeon':  (1, 18),
}

ENEMY_STATS = {
    'slime':    {'name': 'Slime',    'hp': 20,  'atk': 6,  'def': 2,  'exp': 10, 'color': (80, 190, 100)},
    'wolf':     {'name': 'Wolf',     'hp': 35,  'atk': 12, 'def': 4,  'exp': 18, 'color': (130, 100, 80)},
    'skeleton': {'name': 'Skeleton', 'hp': 50,  'atk': 16, 'def': 6,  'exp': 28, 'color': (220, 215, 200)},
    'zombie':   {'name': 'Zombie',   'hp': 65,  'atk': 14, 'def': 8,  'exp': 35, 'color': (100, 160, 80)},
    'boss':     {'name': 'Dark Lord','hp': 200, 'atk': 28, 'def': 12, 'exp': 200,'color': (140, 20, 160)},
}
