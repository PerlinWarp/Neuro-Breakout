## Myo Commons
import struct

def pack(fmt, *args):
    return struct.pack('<' + fmt, *args)

def unpack(fmt, *args):
    return struct.unpack('<' + fmt, *args)

def text(scr, font, txt, pos, clr=(255,255,255)):
    scr.blit(font.render(txt, True, clr), pos)

## Pygame Commons
# Window size
SCALE = int(2)
WIN_X = 800 * SCALE
WIN_Y = 600 * SCALE

# Colours
BLACK = (0,0,0)
WHITE = (255,255,255)
DARKBLUE = (36,90,190)
LIGHTBLUE = (0,176,240)
RED = (255,0,0)
ORANGE = (255,100,0)
YELLOW = (255,255,0)

# Paddle config
PADDLE_X = 100 * SCALE
PADDLE_Y = 10 * SCALE
PADDLE_SPEED = 6 * SCALE

BALL_SIZE = 10 * SCALE


