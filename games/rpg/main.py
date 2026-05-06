#!/usr/bin/env python3
import os

os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ['DISPLAY'] = ':1'

from game import Game

if __name__ == '__main__':
    g = Game()
    g.run()
