#!/usr/bin/env python3
"""Web frontend for PyRPG — streams game frames via MJPEG to the browser."""

import os, sys, io, time, threading, queue
from collections import defaultdict

os.environ['SDL_VIDEODRIVER'] = 'offscreen'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.font.init()

# ── Headless display shim ────────────────────────────────────────────
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE
_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_mode    = lambda *a, **kw: _surface
pygame.display.flip        = lambda: None
pygame.display.set_caption = lambda *a, **kw: None

# ── Key-state shim (for get_pressed polling) ─────────────────────────
_held_keys: set = set()

def _fake_get_pressed():
    result = defaultdict(bool)
    for k in _held_keys:
        result[k] = True
    return result

pygame.key.get_pressed = _fake_get_pressed

# ── Thread-safe event queue (HTTP thread → game thread) ──────────────
# Each item: ('keydown'|'keyup', pg_key_constant)
_key_event_queue: queue.Queue = queue.Queue()

# ── Import game (after shims) ────────────────────────────────────────
from game.game import Game

# ── Shared JPEG frame buffer ─────────────────────────────────────────
_frame_lock  = threading.Lock()
_frame_jpeg: bytes = b''

# JS event.code → pygame key constant
JS_KEY_MAP = {
    'ArrowLeft':  pygame.K_LEFT,
    'ArrowRight': pygame.K_RIGHT,
    'ArrowUp':    pygame.K_UP,
    'ArrowDown':  pygame.K_DOWN,
    'KeyA':       pygame.K_a,
    'KeyD':       pygame.K_d,
    'KeyW':       pygame.K_w,
    'KeyS':       pygame.K_s,
    'KeyE':       pygame.K_e,
    'KeyZ':       pygame.K_z,
    'Enter':      pygame.K_RETURN,
    'Space':      pygame.K_SPACE,
    'Escape':     pygame.K_ESCAPE,
}

def _game_thread():
    global _frame_jpeg
    game  = Game(headless=True)
    clock = pygame.time.Clock()

    while not game._quit_flag:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)

        # Drain the key-event queue and post events into pygame FROM this thread
        while True:
            try:
                kind, pg_key = _key_event_queue.get_nowait()
                if kind == 'keydown':
                    pygame.event.post(pygame.event.Event(
                        pygame.KEYDOWN, key=pg_key, mod=0, unicode='', scancode=0))
                else:
                    pygame.event.post(pygame.event.Event(
                        pygame.KEYUP,   key=pg_key, mod=0, unicode='', scancode=0))
            except queue.Empty:
                break

        try:
            game.step(dt)
        except Exception as e:
            print(f"[game] error: {e}", file=sys.stderr)
            import traceback; traceback.print_exc()
            break

        try:
            buf = io.BytesIO()
            pygame.image.save(_surface, buf, 'jpeg')
            with _frame_lock:
                _frame_jpeg = buf.getvalue()
        except Exception:
            pass

# ── Flask app ────────────────────────────────────────────────────────
from flask import Flask, Response, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title=TITLE)

@app.route('/stream')
def stream():
    def generate():
        while True:
            with _frame_lock:
                data = _frame_jpeg
            if data:
                yield (b'--f\r\nContent-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
            time.sleep(1 / 30)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=f')

@app.route('/input', methods=['POST'])
def handle_input():
    d       = request.get_json(force=True, silent=True) or {}
    js_key  = d.get('key', '')
    pressed = bool(d.get('pressed', False))
    pg_key  = JS_KEY_MAP.get(js_key)

    if pg_key is not None:
        if pressed:
            _held_keys.add(pg_key)
            _key_event_queue.put(('keydown', pg_key))
        else:
            _held_keys.discard(pg_key)
            _key_event_queue.put(('keyup', pg_key))

    return {'ok': True}

if __name__ == '__main__':
    t = threading.Thread(target=_game_thread, daemon=True)
    t.start()
    time.sleep(1.2)

    port = int(os.environ.get('PORT', 5000))
    print(f"[web] PyRPG serving on port {port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
