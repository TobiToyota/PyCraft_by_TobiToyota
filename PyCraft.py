from __future__ import division

import pkg_resources.py2_warn
import sys
import math
import random
import time

#from test import GENERATE

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

from noise_gen import NoiseGen
from noise_gen import NoiseGen_2

from Launcher import GENERATE

#GENERATE = 105571

"""
a = input("Möchtest du einen Seed eingeben? [Y/N] ")
if a == "y" or a == "Y":
    GENERATE = int(input("Welchen Seed? "))
    print("Dein Seed ist jetzt:", GENERATE)
else:
    GENERATE = random.randint(0, 999999999)
    print("Dein Seed ist jetzt:", GENERATE)

"""
    
N = 128
R = 2
fs = True
inv = 0
TICKS_PER_SEC = 60
RENDER_VISION = 5



# Size of sectors used to ease block loading.
SECTOR_SIZE = 16

WALKING_SPEED = 5

FLYING_SPEED = 15
SNEAK_SPEED = WALKING_SPEED / 2

GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.5 # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

PLAYER_HEIGHT = 2

if sys.version_info[0] >= 3:
    xrange = range

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]


def tex_coord(x, y, n=32):
    """ Return the bounding vertices of the texture square.

    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side.

    """

    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)

    return result


inventory_names = "brick grass sand dirt tnt stone glow_stone wool_green wool_blue wool_orange \
    wool_dark_pink wool_pink wool_purple wool_red wool_grey wool_white wool_yellow \
        WOOL_BLACK WOOL_DARK_BLUE WOOL_BROWN WOOL_TURKISE WOOL_DARK_GREY WOOL_DARK_GREEN RANDOM_BLOCK GLASS \
            leaf wood dark_wood SNOW_LAEF snow_grass pig_ore portal_2_ore DIAMOND_ORE iRON_ORE COLE_ORE GOLD_ORE LAPIS_ORE REDSTONE_ORE EMERALD_ORE \
                DIAMOND_BLOCK iRON_BLOCK COLE_BLOCK GOLD_BLOCK LAPIS_BLOCK REDSTONE_BLOCK EMERALD_BLOCK".upper().split()


TEXTURE_PATH = 'textures_0.png' 

x1 = random.randint(0, 31)
x2 = random.randint(0, 31)
x3 = random.randint(0, 31)
y1 = random.randint(13, 31)
y2 = random.randint(13, 31)
y3 = random.randint(13, 31)
TNT = tex_coords((21, 22), (21, 24), (21, 23))
GRASS = tex_coords((26, 13), (8, 25), (12, 21))
DIRT = tex_coords((8, 25), (8, 25), (8, 25))
SAND = tex_coords((19, 24), (19, 24), (19, 24))
BRICK = tex_coords((5, 28), (5, 28), (5, 28))
STONE = tex_coords((20, 22), (20, 22), (20, 22))
BEDROCK = tex_coords((4, 28), (4, 28), (4, 28))
GLASS = tex_coords((7, 23), (7, 23), (7, 23))
GLOW_STONE = tex_coords((9, 21), (9, 21), (9, 21))
WOOL_GREEN = tex_coords((23, 30), (23, 30), (23, 30))
WOOL_BLUE = tex_coords((23, 31), (23, 31), (23, 31))
WOOL_DARK_PINK = tex_coords((23, 29), (23, 29), (23, 29))
WOOL_ORANGE = tex_coords((23, 28), (23, 28), (23, 28))
WOOL_PINK = tex_coords((23, 27), (23, 27), (23, 27))
WOOL_PURPLE = tex_coords((23, 26), (23, 26), (23, 26))
WOOL_RED = tex_coords((23, 25), (23, 25), (23, 25))
WOOL_GREY = tex_coords((23, 24), (23, 24), (23, 24))
WOOL_WHITE = tex_coords((23, 23), (23, 23), (23, 23))
WOOL_YELLOW = tex_coords((23, 22), (23, 22), (23, 22))
WOOL_BLACK = tex_coords((22, 21), (22, 21), (22, 21))
WOOL_DARK_BLUE = tex_coords((22, 20), (22, 20), (22, 20))
WOOL_BROWN = tex_coords((22, 19), (22, 19), (22, 19))
WOOL_TURKISE = tex_coords((22, 18), (22, 18), (22, 18))
WOOL_DARK_GREY = tex_coords((22, 17), (22, 17), (22, 17))
WOOL_DARK_GREEN = tex_coords((22, 16), (22, 16), (22, 16))
random_block = tex_coords((x1, y1), (x2, y2), (x3, y3))
WOOD = tex_coords((4, 17), (4, 17), (3, 17))
DARK_WOOD = tex_coords((6, 17), (6, 17), (5, 17))
LAEF = tex_coords((4, 18), (4, 18), (4, 18))
SNOW_LAEF = tex_coords((5, 18), (5, 18), (5, 18))
BARRIER = tex_coords((0, 0), (0, 0), (0, 0))
WATER = tex_coords((3, 31), (3, 30), (3, 30))
PIG = tex_coords((27, 13), (27, 13), (27, 13))
SNOW_GRASS = tex_coords((20, 26), (8, 25), (14, 21))
DIAMOND_ORE = tex_coords((8, 26), (8, 26), (8, 26))
DIAMOND_BLOCK = tex_coords((8, 27), (8, 27), (8, 27))
IRON_ORE = tex_coords((11, 19), (11, 19), (11, 19))
IRON_BLOCK = tex_coords((10, 19), (10, 19), (10, 19))
COLE_ORE = tex_coords((1, 26), (1, 26), (1, 26))
COLE_BLOCK = tex_coords((0, 26), (0, 26), (0, 26))
GOLD_ORE = tex_coords((11, 21), (11, 21), (11, 21))
GOLD_BLOCK = tex_coords((10, 21), (10, 21), (10, 21))
LAPIS_ORE = tex_coords((2, 18), (2, 18), (2, 18))
LAPIS_BLOCK = tex_coords((1, 18), (1, 18), (1, 18))
REDSTONE_ORE = tex_coords((19, 30), (19, 30), (19, 30))
REDSTONE_BLOCK = tex_coords((18, 21), (18, 21), (18, 21))
EMERALD_ORE = tex_coords((13, 28), (13, 28), (13, 28))
EMERALD_BLOCK = tex_coords((13, 29), (13, 29), (13, 29))
PORTAL_2 = tex_coords((28, 13), (28, 13), (28, 13))
BREAK_BLOCK = tex_coords((8, 30), (8, 30), (8, 30))

ores = [DIAMOND_ORE, IRON_ORE, COLE_ORE, GOLD_ORE, LAPIS_ORE, REDSTONE_ORE, EMERALD_ORE]
ores_names = "DIAMOND_ORE IRON_ORE COLE_ORE GOLD_ORE LAPIS_ORE REDSTONE_ORE EMERALD_ORE".split()




FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]


def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


def sectorize(position):
    """ Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)



class Model(object):

    def __init__(self):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()
        

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        #self.chunks = []
        #self.Chunk(0, 0)
        
        self.heightMap = []
        #self.Entity()
        self.initialize()
        #self.initialize_cave()
        self.Ores()
        self.DigMines()
        

        

    def Entity(self):
        self.add_block_mini((N // 2, HEIGHTMAP + 3, N // 2), PIG)



    def Chunk(self, x_pos, z_pos):
        pos1 = x_pos
        pos2 = z_pos
        s = R * 8
        size = 16
        for x in range(size):
            for y in range(size):
                y += 20
                for z in range(size):
                    self.add_block((x - pos1, y - 19, z - pos2), STONE, immediate=False)
            for y in range(3):
                y += 20
                for z in range(size):
                    self.add_block((x - pos1, y - 5, z - pos2), DIRT, immediate=False)
            for y in range(1):
                y += 20
                for z in range(size):
                    self.add_block((x - pos1, y - 2, z - pos2), GRASS, immediate=False)
                for z in range(size):
                    self.add_block((x - pos1, y - 20, z - pos2), BEDROCK, immediate=False)
                                                
        #x = -R * 16 
        #y = 0
        #z = R * 16
        #for t in range(R * 16):
            #for l in range(R * 16):
                #for dy in xrange(-20, 20):
                    #self.add_block((x, y + dy, z - t), BARRIER, immediate=False)
                #for dy in xrange(-20, 20):
                    #self.add_block((x + z, y + dy, z - t), BARRIER, immediate=False)
                #for dy in xrange(-20, 20):
                    #self.add_block((x - -l, y + dy, z), BARRIER, immediate=False)
                #for dy in xrange(-20, 20):
                    #self.add_block((x - -l, y + dy, z + x), BARRIER, immediate=False)
        

    def Tree(self):
        y = -1
        o = R * 16 - 3
        a = random.randint(-o, -3)
        b = random.randint(3, o)
        self.add_block((a, y, b), WOOD, immediate=False)
        self.add_block((a, y + 1, b), WOOD, immediate=False)
        self.add_block((a, y + 2, b), WOOD, immediate=False)
        self.add_block((a, y + 3, b), WOOD, immediate=False)
        
        for x in range(2):
            x = x
            self.add_block((a + 1, y + 2 + x, b), LAEF, immediate=False)
            self.add_block((a - 1, y + 2 + x, b), LAEF, immediate=False)
            self.add_block((a, y + 2 + x, b + 1), LAEF, immediate=False)
            self.add_block((a, y + 2 + x, b - 1), LAEF, immediate=False)
            self.add_block((a + 1, y + 2 + x, b + 1), LAEF, immediate=False)
            self.add_block((a - 1, y + 2 + x, b - 1), LAEF, immediate=False)
            self.add_block((a + 1, y + 2 + x, b - 1), LAEF, immediate=False)
            self.add_block((a - 1, y + 2 + x, b + 1), LAEF, immediate=False)
            self.add_block((a, y + 2 + x, b - 2), LAEF, immediate=False)
            self.add_block((a - 1, y + 2 + x, b - 2), LAEF, immediate=False)
            self.add_block((a + 1, y + 2 + x, b - 2), LAEF, immediate=False)
            self.add_block((a, y + 2 + x, b + 2), LAEF, immediate=False)
            self.add_block((a - 1, y + 2 + x, b + 2), LAEF, immediate=False)
            self.add_block((a + 1, y + 2 + x, b + 2), LAEF, immediate=False)
            self.add_block((a - 2, y + 2 + x, b), LAEF, immediate=False)
            self.add_block((a - 2, y + 2 + x, b - 1), LAEF, immediate=False)
            self.add_block((a - 2, y + 2 + x, b + 1), LAEF, immediate=False)
            self.add_block((a + 2, y + 2 + x, b), LAEF, immediate=False)
            self.add_block((a + 2, y + 2 + x, b - 1), LAEF, immediate=False)
            self.add_block((a + 2, y + 2 + x, b + 1), LAEF, immediate=False)
            self.add_block((a + 1, y + 4, b), LAEF, immediate=False)
            self.add_block((a - 1, y + 4, b), LAEF, immediate=False)
            self.add_block((a, y + 4, b + 1), LAEF, immediate=False)
            self.add_block((a, y + 4, b - 1), LAEF, immediate=False)
            self.add_block((a + 1, y + 4, b + 1), LAEF, immediate=False)
            self.add_block((a - 1, y + 4, b - 1), LAEF, immediate=False)
            self.add_block((a + 1, y + 4, b - 1), LAEF, immediate=False)
            self.add_block((a - 1, y + 4, b + 1), LAEF, immediate=False)
            self.add_block((a, y + 4, b), LAEF, immediate=False)
    
    gen = NoiseGen(105571)
    def initialize(self):
        
        if GENERATE == 17052007:
            self._initialize()
        
        else:
            #gen = NoiseGen(105581)
            gen = NoiseGen(GENERATE)
            n = N  #size of the world
            s = 1  # step size
            y = 0  # initial y height
                #too lazy to do this properly lol
            self.heightMap = []
            for x in xrange(0, n, s):
                for z in xrange(0, n, s):
                    self.heightMap.append(0)
            for x in xrange(0, n, s):
                for z in xrange(0, n, s):
                    self.heightMap[z + x * n] = int(gen.getHeight(x, z))
 
                

                #Generate the world
            for x in xrange(0, n, s):
                for z in xrange(0, n, s):
                    h = self.heightMap[z + x * n] + 20
                    if (h < 35):
                        for y in range(h, 35):
                            #self.add_Water((x, y, z), WATER)
                            self.add_block((x, h, z), SAND, immediate=False)
                            self.add_block((x, h - 1, z), SAND, immediate=False)
                            self.add_block((x, h - 2, z), SAND, immediate=False)
                        for y in xrange(h - 3, 0, -1):
                            self.add_block((x, y, z), STONE, immediate=False)
                        self.add_block((x, 0, z), BEDROCK, immediate=False)
                        continue
                    if (h < 38):
                        self.add_block((x, h, z), SAND, immediate=False)
                        print(x, h, z)
                    if (h < 70):
                        self.add_block((x, h, z), GRASS, immediate=False)
                    else:
                        self.add_block((x, h, z), SNOW_GRASS, immediate=False)
                    for y in xrange(h - 2, 0, -1):
                        self.add_block((x, y, z), STONE, immediate=False)
                    for y in xrange(h - 1, h - 2, -1):
                        self.add_block((x, y, z), DIRT, immediate=False)
                    self.add_block((x, 0, z), BEDROCK, immediate=False)
                    #Maybe add tree at this (x, z)
                    
                    if (h > 40):
                        if random.randrange(0, 1000) > 990:
                            treeHeight = random.randrange(4, 7)
                            #Tree trunk
                            #for y in xrange(h + 1, h + treeHeight):
                            #    self.add_block((x, y, z), WOOD, immediate=False)
                            #Tree leaves
                            if h + 1 > 70:
                                for y in xrange(h + 1, h + treeHeight):
                                    self.add_block((x, y, z), DARK_WOOD, immediate=False)
                            else:
                                for y in xrange(h + 1, h + treeHeight):
                                    self.add_block((x, y, z), WOOD, immediate=False)
                            leafh = h + treeHeight
                            if leafh - 3 > 70:
                                if treeHeight >= 6:
                                    for i in range(3):
                                        i += 1
                                        self.add_block((x + 1, leafh - i, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z - 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z - 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z - 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z + 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z + 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z + 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh, z), SNOW_LAEF, immediate=False)
                                else:
                                    for i in range(2):
                                        i += 1
                                        self.add_block((x + 1, leafh - i, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z - 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z - 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z - 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z + 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z + 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z + 2), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z - 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z + 1), SNOW_LAEF, immediate=False)
                                        self.add_block((x, leafh, z), SNOW_LAEF, immediate=False)
                            else:
                                if treeHeight >= 6:
                                    for i in range(3):
                                        i += 1
                                        self.add_block((x + 1, leafh - i, z), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z), LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z - 2), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z - 2), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z - 2), LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z + 2), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z + 2), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z + 2), LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z), LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z), LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z), LAEF, immediate=False)
                                        self.add_block((x, leafh, z + 1), LAEF, immediate=False)
                                        self.add_block((x, leafh, z - 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z + 1), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z - 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z - 1), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z + 1), LAEF, immediate=False)
                                        self.add_block((x, leafh, z), LAEF, immediate=False)
                                else:
                                    for i in range(2):
                                        i += 1
                                        self.add_block((x + 1, leafh - i, z), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z), LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z - 2), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z - 2), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z - 2), LAEF, immediate=False)
                                        self.add_block((x, leafh - i, z + 2), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh - i, z + 2), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh - i, z + 2), LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z), LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x - 2, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z), LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z - 1), LAEF, immediate=False)
                                        self.add_block((x + 2, leafh - i, z + 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z), LAEF, immediate=False)
                                        self.add_block((x, leafh, z + 1), LAEF, immediate=False)
                                        self.add_block((x, leafh, z - 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z + 1), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z - 1), LAEF, immediate=False)
                                        self.add_block((x + 1, leafh, z - 1), LAEF, immediate=False)
                                        self.add_block((x - 1, leafh, z + 1), LAEF, immediate=False)
                                        self.add_block((x, leafh, z), LAEF, immediate=False)
    """
    def initialize_cave(self):
            
        if GENERATE == 17052007:
            self._initialize()
        
        else:
            #gen = NoiseGen(105581)
            #gen = NoiseGen(GENERATE)
            n = N  #size of the world
            s = 1  # step size
            y = 0  # initial y height
                #too lazy to do this properly lol
            gen = NoiseGen(GENERATE)
            CaveMap = self.heightMap
            for x in xrange(0, n, s):
                for z in xrange(0, n, s):
                    CaveMap.append(0)
            for x in xrange(0, n, s):
                for z in xrange(0, n, s):
                    CaveMap[z + x * n] = int(gen.getHeight(x, z))

            gen_2 = NoiseGen_2(GENERATE)
            CaveMap_2 = []
            for x in xrange(0, n, s):
                for z in xrange(0, n, s):
                    CaveMap_2.append(0)
            for x in xrange(0, n, s):
                for z in xrange(0, n, s):
                    CaveMap_2[z + x * n] = int(gen_2.getHeight_2(x, z))

            
            for x in xrange(0, n, s):
                for z in xrange(0, n, s):
                    h = CaveMap[z + x * n] + 18
                    h_2 = CaveMap_2[z + x * n]
                    if h_2 > h - 10:
                        h_2 -= h
                    #print(h_2, -h_2)
                    #print(x, h, z)
                        
                     
                    
                    for y in xrange(h_2 - 2, h - 10, 1):
                        if y < 1:
                            y = 1
                        print(x, y, z)
                        #print(1)
                        self.add_block((x, y, z), STONE, immediate=False)
                        #self.remove_block((x, y, z))
                        
                    for y in xrange(h_2 - 5, h - 10, 1):
                        if y < 1:
                            y = 1
                        print(x, y, z)
                        #print(1)
                        self.add_block((x, y, z), STONE, immediate=False)
                        self.remove_block((x, y, z))
                    
                    for y in xrange(h // 2 + h // 4 - 10, h // 2 + h // 4 + 10, 1):
                        if y < 1:
                            y = 1
                        print(x, y, z)
                        print(2)
                        self.add_block((x, y, z), STONE, immediate=False)
                        self.remove_block((x, y, z))
                        

                    
                    
                    if h >= h_2:    
                        for y in range(h - 10, h_2 + 10, -1):
                            if y <= 0:
                                y = 1
                            print(x, y, z)
                            self.remove_block((x, y, z))
                    else:
                        for y in range(h_2 - 10, h + 10, 1):
                            if y <= 0:
                                y = 1
                            print(x, y, z)
                            self.remove_block((x, y, z))
                    
                    for y in range(h - 10, h - 20, -1):
                        if y <= 0:
                            y = 1
                        self.add_block((x, y, z), STONE, immediate=False)

                    for y in range(h_2 + 10, h_2 + 20, 1):
                        if y <= 0:
                            y = 1
                        self.add_block((x, y, z), STONE, immediate=False)
                    
                    for y in range(h_2 - 10, h_2 - 20, -1):
                        if y <= 0:
                            y = 1
                        self.add_block((x, y, z), STONE, immediate=False)

                    for y in range(h_2 + 10, h_2 + 20, 1):
                        if y <= 0:
                            y = 1
                        self.add_block((x, y, z), STONE, immediate=False)
                    """
                    
                    


    def DigMines(self,mines=N // 4):
        for i in range(mines):
            s = random.randint(3, 5)
            s_1 = random.randint(1, 4)
            X,Z = random.randint(10, N - 10),random.randint(10, N - 10)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) + 10
            if y_2 < 11:
                y_2 = 11
            Y = random.randint(10, y_2)
            for j in range(random.randint(20, 75)):
                s = random.randint(3, 5)
                s_1 = random.randint(1, 4)
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            if x or y or z: self.add_block((X+x,Y+y,Z+z), BRICK, immediate=False)
                            if x or y or z: self.remove_block((X+x,Y+y,Z+z))
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
    
    def Ores(self):
        for cole in range((N + N // 2) * 2):
            self.COLE()
        for iron in range((N // 2 + N // 4 + N // 6) * 2):
            self.IRON()
        for gold in range((N // 4 + N // 6 + N // 8) * 2):
            self.GOLD()
        for redstone in range((N // 4 + N // 6 + N // 8) * 2):
            self.REDSTONE()
        for lapis in range((N // 4 + N // 6 + N // 8) * 2):
            self.LAPIS()
        for diamond in range((N // 4 + N // 6) * 2):
            self.Diamond()
            self.Portal_2_Ore()
            self.PIG_ORE()
        for emerald in range((N // 8 + N // 6)):
            self.EMERALD()

    def IRON(self, ore=1):
        s = random.randint(1,2)
        s_1 = random.randint(0,1)
        size = random.randint(1,4)
        for i in range(ore):
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) + 12
            if y_2 <= 2:
                y_2 = 3
            Y = random.randint(2, y_2)
            for j in range(size):
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            self.add_block((X+x,Y+y,Z+z), IRON_ORE, immediate=False)
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) + 12:
                    Y = int(gen.getHeight(X, Z)) + 12

    def Diamond(self, ore=1):
        s = random.randint(1,2)
        s_1 = random.randint(0,1)
        for i in range(ore):
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) - 3
            if y_2 <= 2:
                y_2 = 3
            if y_2 > 13:
                y_2 = 13
            Y = random.randint(2, y_2)
            for j in range(1):
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            self.add_block((X+x,Y+y,Z+z), DIAMOND_ORE, immediate=False)
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) - 3:
                    Y = int(gen.getHeight(X, Z)) - 3
                if Y > 13:
                    Y = 13
    
    def Portal_2_Ore(self, ore=1):
        s = random.randint(1,2)
        s_1 = random.randint(0,1)
        for i in range(ore):
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) - 3
            if y_2 <= 2:
                y_2 = 3
            if y_2 > 13:
                y_2 = 13
            Y = random.randint(2, y_2)
            for j in range(1):
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            self.add_block((X+x,Y+y,Z+z), PORTAL_2, immediate=False)
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) - 3:
                    Y = int(gen.getHeight(X, Z)) - 3
                if Y > 13:
                    Y = 13

    def REDSTONE(self, ore=1):
        s = random.randint(1,2)
        s_1 = random.randint(0,1)
        size = random.randint(1,2)
        for i in range(ore):
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) + 5
            if y_2 <= 2:
                y_2 = 3
            if y_2 > 30:
                y_2 = 30
            Y = random.randint(2, y_2)
            for j in range(size):
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            self.add_block((X+x,Y+y,Z+z), REDSTONE_ORE, immediate=False)
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) + 5:
                    Y = int(gen.getHeight(X, Z)) + 5
                if Y > 30:
                    Y = 30

    def EMERALD(self, ore=1):
        s = 2
        for i in range(ore):
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) - 3
            if y_2 <= 2:
                y_2 = 3
            if y_2 > 10:
                y_2 = 10
            Y = random.randint(2, y_2)
            for j in range(1):
                for x in range(1,s):
                    for y in range(1,s):
                        for z in range(1,s):
                            self.add_block((X+x,Y+y,Z+z), EMERALD_ORE, immediate=False)

                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) - 3:
                    Y = int(gen.getHeight(X, Z)) - 3
                if Y > 10:
                    Y = 10

    def GOLD(self, ore=1):
        s = random.randint(1,2)
        s_1 = random.randint(0,1)
        size = random.randint(1,2)
        for i in range(ore):
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) + 3
            if y_2 <= 2:
                y_2 = 3
            if y_2 > 30:
                y_2 = 30
            Y = random.randint(2, y_2)
            for j in range(size):
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            self.add_block((X+x,Y+y,Z+z), GOLD_ORE, immediate=False)
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) + 3:
                    Y = int(gen.getHeight(X, Z)) + 3
                if Y > 30:
                    Y = 30

    def LAPIS(self, ore=1):
        s = random.randint(1,2)
        s_1 = random.randint(0,1)
        size = random.randint(1,2)
        for i in range(ore):
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) + 3
            if y_2 <= 2:
                y_2 = 3
            if y_2 > 25:
                y_2 = 25
            Y = random.randint(2, y_2)
            for j in range(size):
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            self.add_block((X+x,Y+y,Z+z), LAPIS_ORE, immediate=False)
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) + 3:
                    Y = int(gen.getHeight(X, Z)) + 3
                if Y > 25:
                    Y = 25

    def COLE(self, ore=1):
        size = random.randint(1, 6)
        for i in range(ore):
            s = random.randint(1,2)
            s_1 = random.randint(0,1)
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) + 15
            if y_2 <= 2:
                y_2 = 3
            Y = random.randint(2, y_2)
            for j in range(size):
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            self.add_block((X+x,Y+y,Z+z), COLE_ORE, immediate=False)
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) + 15:
                    Y = int(gen.getHeight(X, Z)) + 15

    def PIG_ORE(self, ore=1):
        s = random.randint(1,2)
        s_1 = random.randint(0,1)
        for i in range(ore):
            X,Z = random.randint(1, N - 2),random.randint(1, N - 2)
            gen = NoiseGen(GENERATE)
            y_2 = int(gen.getHeight(X, Z)) - 3
            if y_2 <= 2:
                y_2 = 3
            if y_2 > 13:
                y_2 = 13
            Y = random.randint(2, y_2)
            for j in range(1):
                for x in range(s_1,s):
                    for y in range(s_1,s):
                        for z in range(s_1,s):
                            self.add_block((X+x,Y+y,Z+z), PIG)
                X+=random.randrange(-1,2); Y+=random.randrange(-1,2); Z+=random.randrange(-1,2)
                if s>X or s>=N-X: X = N/2
                if s>Y or s>=N-Y: Y = N/2
                if s>Z or s>=N-Z: Z = N/2
                if Y > int(gen.getHeight(X, Z)) - 3:
                    Y = int(gen.getHeight(X, Z)) - 3
                if Y > 13:
                    Y = 13



    def _initialize(self):
        """ Initialize the world by placing all the blocks.

        """
        
         # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        self.Chunk(0, 0)
        for x in range(10):
            self.Tree()
        # generate the hills randomly
        o = R * 16 - 10
        #for _ in xrange(10):
        #    a = random.randint(-o, 0)  # x position of the hill
        #    b = random.randint(0, o)  # z position of the hill
        #    c = -1  # base of the hill
        #    h = random.randint(3, 10)  # height of the hill
        #    s = random.randint(4, 10)  # 2 * s is the side length of the hill
        #    d = 1  # how quickly to taper off the hills
            
            
        #    for y in xrange(c, c + h):
        #        for x in xrange(a - s, a + s + 1):
        #            for z in xrange(b - s, b + s + 1):
        #                if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
        #                    continue
        #                if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
        #                    continue
        #                
        #                self.add_block((x, y, z), GRASS, immediate=False)
        #                self.add_block((x, y - 1, z), DIRT, immediate=False)
        #                self.add_block((x, y - 2, z), STONE, immediate=False)
        #                self.add_block((x, c - 1, z), STONE, immediate=False)
        #                self.add_block((x, c - 2, z), STONE, immediate=False)
        #                self.add_block((x, c - 3, z), STONE, immediate=False)
        #                self.add_block((x, c - 4, z), STONE, immediate=False)
                        
                        
                        
        #        s -= d  # decrement side lenth so hills taper off


        
        

    def hit_test(self, position, vector, max_distance=5):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 5
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False


    def add_entity(self, position, texture):
        if position in self.world:
            self.remove_block(position)
        self.world[position] = texture
        if self.exposed(position):
            self.show_block(position)
            

    def add_Water(self, position, texture, immediate=True):
        #if position in self.world:
            #self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        #if self.exposed(position):
            #self.show_Water(position)
        if immediate:
            self.check_neighbors(position)


    def add_block(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def add_block_mini(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block_mini(position)
            self.check_neighbors(position)


    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)
            

            

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def show_block_mini(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block_mini(position, texture)
        else:
            self._enqueue(self._show_block_mini, position, texture)

    def show_Water(self, position, immediate=False):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        texture = WATER
        self.shown[position] = texture
        if immediate:
            self._show_Water(position, texture)
        else:
            self._enqueue(self._show_Water, position, texture)


    def _show_block(self, position, texture):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.

        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def _show_block_mini(self, position, texture):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.

        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.25)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def _show_Water(self, position, texture):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.

        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.time()
        while self.queue and time.time() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()


class entity():
    def __init__(self):

        #if GENERATE != 17052007:
            #self.position = (N / 2, HEIGHTMAP + 1, N / 2)
        #else:
            #self.position = (-R * 8, 0, R * 8)

        self.strafe = [0, 0]

        self.rotation = (0, 0)

        self.dy = 0


    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        
        m = 4
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        
        speed = 5
        d = dt * speed # distance covered this tick.s
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt
        # collisions
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)

    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        x, y, z = self.position
        for face in FACES:
              # check all surrounding blocks 
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                if self.sneaking:
                    for dy in xrange(height):  # check each height
                        op = list(np)
                        op[1] -= dy
                        op[i] += face[i]
                        if tuple(op) not in self.model.world:
                            continue
                        p[i] -= (d - pad) * face[i]
                        p[1] -= 0.2
                        if p[1] <= int(p[1]) + 0.5:
                            p[1] = int(p[1]) + 0.55
                        if face == (0, -1, 0) or face == (0, 1, 0):
                            # You are colliding with the ground or ceiling, so stop
                            # falling / rising.
                            self.dy = 0
                        if face != (0, -1, 0):
                            p[1] = int(p[1]) + 0.55
                            if face == (0, 0, 1):
                                print(1)
                                p[2] = int(p[2]) + 0.3
                                if p[2] < int(p[2]) + 0.3:
                                    p[2] = int(p[2]) + 0.3
                                p[1] = int(p[1]) + 0.6
                            if face == (0, 0, -1):
                                print(2)
                                p[2] = int(p[2]) + 1 - 0.3
                                if p[2] < int(p[2]) + 1 - 0.3:
                                    p[2] = int(p[2]) + 1 - 0.3
                                p[1] = int(p[1]) + 0.6
                            if face == (1, 0, 0):
                                print(3)
                                p[0] = int(p[0]) + 0.3
                                if p[0] < int(p[0]) + 0.3:
                                    p[0] = int(p[0]) + 0.3
                                p[1] = int(p[1]) + 0.6
                            if face == (-1, 0, 0):
                                print(4)
                                p[0] = int(p[0]) + 1 - 0.3
                                if p[0] < int(p[0]) + 1 - 0.3:
                                    p[0] = int(p[0]) + 1 - 0.3
                                p[1] = int(p[1]) + 0.6
                        break
                elif self.modus == 3:
                    for dy in xrange(height):  # check each height
                        op = list(np)
                        op[1] -= dy
                        op[i] += face[i]
                        
                else:
                    for dy in xrange(height):  # check each height
                        op = list(np)
                        op[1] -= dy
                        op[i] += face[i]
                        if tuple(op) not in self.model.world:
                            continue
                        p[i] -= (d - pad) * face[i]
                        if face == (0, -1, 0) or face == (0, 1, 0):
                            # You are colliding with the ground or ceiling, so stop
                            # falling / rising.
                            self.dy = 0
                        break
        return tuple(p)


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # When flying gravity has no effect and speed is increased.
        self.flying = False

        self.running = False

        self.sneaking = False

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.

        gen = NoiseGen(GENERATE)
        HEIGHTMAP = int(gen.getHeight(N / 2, N / 2)) + 20

        if GENERATE != 17052007:
            if HEIGHTMAP < 0:
                self.position = (N / 2, 0 + PLAYER_HEIGHT, N / 2)
            else:
                self.position = (N / 2, HEIGHTMAP + PLAYER_HEIGHT, N / 2)
        else:
            self.position = (8, 20, 8)
        #self.position = (0, 0, 0)


        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle = None

        # Velocity in the y (upward) direction.
        self.dy = 0

        
        self.modus = 1
        # A list of blocks the player can place. Hit num keys to cycle.
        self.creative_inventory = [BRICK, GRASS, SAND, DIRT, TNT, STONE, GLOW_STONE, WOOL_GREEN, WOOL_BLUE, WOOL_ORANGE,
                            WOOL_DARK_PINK, WOOL_PINK, WOOL_PURPLE, WOOL_RED, WOOL_GREY, WOOL_WHITE, WOOL_YELLOW, 
                            WOOL_BLACK, WOOL_DARK_BLUE, WOOL_BROWN, WOOL_TURKISE, WOOL_DARK_GREY, WOOL_DARK_GREEN, 
                            random_block, GLASS, LAEF, WOOD, DARK_WOOD, SNOW_LAEF, SNOW_GRASS, PIG, PORTAL_2, DIAMOND_ORE, IRON_ORE,
                            COLE_ORE, GOLD_ORE, LAPIS_ORE, REDSTONE_ORE, EMERALD_ORE, DIAMOND_BLOCK, IRON_BLOCK,
                            COLE_BLOCK, GOLD_BLOCK, LAPIS_BLOCK, REDSTONE_BLOCK, EMERALD_BLOCK]
        
        self.surv_inv = [BRICK, 0, GRASS, 0, SAND, 0, DIRT, 0, TNT, 0, STONE, 0, GLOW_STONE, 0, WOOL_GREEN, 0, WOOL_BLUE, 0, WOOL_ORANGE, 0,
                            WOOL_DARK_PINK, 0, WOOL_PINK, 0, WOOL_PURPLE, 0, WOOL_RED, 0, WOOL_GREY, 0, WOOL_WHITE, 0, WOOL_YELLOW, 0, 
                            WOOL_BLACK, 0, WOOL_DARK_BLUE, 0, WOOL_BROWN, 0, WOOL_TURKISE, 0, WOOL_DARK_GREY, 0, WOOL_DARK_GREEN, 0,
                            random_block, 0, GLASS, 0, LAEF, 0, WOOD, 0, DARK_WOOD, 0, SNOW_LAEF, 0, SNOW_GRASS, 0, PIG, 0, PORTAL_2, 0, DIAMOND_ORE, 0, IRON_ORE, 0,
                            COLE_ORE, 0, GOLD_ORE, 0, LAPIS_ORE, 0, REDSTONE_ORE, 0, EMERALD_ORE, 0, DIAMOND_BLOCK, 0, IRON_BLOCK, 0,
                            COLE_BLOCK, 0, GOLD_BLOCK, 0, LAPIS_BLOCK, 0, REDSTONE_BLOCK, 0, EMERALD_BLOCK, 0]


        self.inv = inv

        self.modus_names = "survival creative spectator".upper().split()

        self.chunks = []
        self.world_size = 16
        
        # The current block the user can place. Hit num keys to cycle.
        self.block = self.creative_inventory[self.inv]
        #self.block = self.surv_inv[0]

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        
        self.model = Model()

        entity()

        # The label that is displayed in the top left of the canvas.
        self.label_1 = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))

        self.label_2 = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10  , anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        
        self.label_3 = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10  , anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

        

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying or self.modus == 3:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        self.model.process_queue()
        sector = sectorize(self.position)
        #print(sector, self.sector, self.position)
        self.chunks.append(sector)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
            self.chunks.append(self.sector)

        self.sector = sector
        self.model.show_sector(self.sector)

        """
        #print(self.sector)
        for i in range(2):
            i += 1
            self.sector = self.sector[:0] + (self.sector[0] + i,) + self.sector[1:]
            if self.sector not in self.chunks:
                self.model.process_entire_queue()
                self.x = (self.sector[0]) * 16
                self.world_size += 16
                self.model.initialize(self.x, 0, self.world_size)
                self.model.process_entire_queue()
                self.chunks.append(self.sector)
                self.model.show_sector(self.sector)
                print(1, i)
            self.sector = self.sector[:0] + (self.sector[0] - i,) + self.sector[1:]

            self.sector = self.sector[:0] + (self.sector[0] - i,) + self.sector[1:]
            if self.sector not in self.chunks:
                self.model.process_entire_queue()
                self.x = (self.sector[0]) * 16
                self.world_size += 16
                self.model.initialize(self.x, 0, self.world_size)
                self.model.process_entire_queue()
                self.chunks.append(self.sector)
                self.model.show_sector(self.sector)
                print(2, i)
            self.sector = self.sector[:0] + (self.sector[0] + i,) + self.sector[1:]

            self.sector = self.sector[:2] + (self.sector[2] + i,)
            if self.sector not in self.chunks:
                self.model.process_entire_queue()
                self.z = (self.sector[2]) * 16
                self.world_size += 16
                self.model.initialize(0, self.z, self.world_size)
                self.model.process_entire_queue()
                self.chunks.append(self.sector)
                self.model.show_sector(self.sector)
                print(3, i)
            self.sector = self.sector[:2] + (self.sector[2] - i,)

            self.sector = self.sector[:2] + (self.sector[2] - i,)
            if self.sector not in self.chunks:
                self.model.process_entire_queue()
                self.z = (self.sector[2]) * 16
                self.world_size += 16
                self.model.initialize(0, self.z, self.world_size)
                self.model.process_entire_queue()
                self.chunks.append(self.sector)
                self.model.show_sector(self.sector)
                print(4, i)
            self.sector = self.sector[:2] + (self.sector[2] + i,)

            self.sector = self.sector[:2] + (self.sector[2] - i,)
            self.sector = self.sector[:0] + (self.sector[0] + i,) + self.sector[1:]
            if self.sector not in self.chunks:
                self.model.process_entire_queue()
                self.z = (self.sector[2]) * 16
                self.x = (self.sector[0]) * 16
                self.world_size += 16
                self.model.initialize(self.x, self.z, self.world_size)
                self.model.process_entire_queue()
                self.chunks.append(self.sector)
                self.model.show_sector(self.sector)
                print(5, i)
            self.sector = self.sector[:2] + (self.sector[2] + i,)
            self.sector = self.sector[:0] + (self.sector[0] - i,) + self.sector[1:]

            self.sector = self.sector[:2] + (self.sector[2] + i,)
            self.sector = self.sector[:0] + (self.sector[0] - i,) + self.sector[1:]
            if self.sector not in self.chunks:
                self.model.process_entire_queue()
                self.z = (self.sector[2]) * 16
                self.x = (self.sector[0]) * 16
                self.world_size += 16
                self.model.initialize(self.x, self.z, self.world_size)
                self.model.process_entire_queue()
                self.chunks.append(self.sector)
                self.model.show_sector(self.sector)
                print(6, i)
            self.sector = self.sector[:2] + (self.sector[2] - i,)
            self.sector = self.sector[:0] + (self.sector[0] + i,) + self.sector[1:]

            self.sector = self.sector[:2] + (self.sector[2] + i,)
            self.sector = self.sector[:0] + (self.sector[0] + i,) + self.sector[1:]
            if self.sector not in self.chunks:
                self.model.process_entire_queue()
                self.z = (self.sector[2]) * 16
                self.x = (self.sector[0]) * 16
                self.world_size += 16
                self.model.initialize(self.x, self.z, self.world_size)
                self.model.process_entire_queue()
                self.chunks.append(self.sector)
                self.model.show_sector(self.sector)
                print(7, i)
            self.sector = self.sector[:2] + (self.sector[2] - i,)
            self.sector = self.sector[:0] + (self.sector[0] - i,) + self.sector[1:]

            self.sector = self.sector[:2] + (self.sector[2] - i,)
            self.sector = self.sector[:0] + (self.sector[0] - i,) + self.sector[1:]
            if self.sector not in self.chunks:
                self.model.process_entire_queue()
                self.z = (self.sector[2]) * 16
                self.x = (self.sector[0]) * 16
                self.world_size += 16
                self.model.initialize(self.x, self.z, self.world_size)
                self.model.process_entire_queue()
                self.chunks.append(self.sector)
                self.model.show_sector(self.sector)
                print(8, i)
            self.sector = self.sector[:2] + (self.sector[2] + i,)
            self.sector = self.sector[:0] + (self.sector[0] + i,) + self.sector[1:]

        if self.sector not in self.chunks:
            self.model.process_entire_queue()
            self.z = (self.sector[2]) * 16
            self.world_size += 16
            self.model.initialize(0, self.z, self.world_size)
            self.model.process_entire_queue()
            self.chunks.append(self.sector)
            self.model.show_sector(self.sector)
            print(10)
        """
        
        p = list(self.position)
        gen = NoiseGen(GENERATE)
        y = int(gen.getHeight(p[0], p[2])) + 100
        if p[1] < -100:
            p[1] = y
        if p[1] > 200:
            p[1] = -100
        if p[0] > N + 60:
            p[0] = -60
        if p[0] < -60:
            p[0] = N + 60
        if p[2] > N + 60:
            p[2] = -60
        if p[2] < -60:
            p[2] = N + 60
        x, y, z = p
        self.position = (x, y, z)
        m = 4
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        
        if self.flying:
            speed = FLYING_SPEED
            current_speed = FLYING_SPEED
            if self.running:
                speed = current_speed * 2
        elif self.sneaking and not self.flying and not self.running:
            speed = SNEAK_SPEED
        elif self.running and not self.sneaking:
            speed = WALKING_SPEED
            current_speed = WALKING_SPEED
            speed = current_speed * 1.5
        else:
            speed = WALKING_SPEED
            current_speed = WALKING_SPEED
        d = dt * speed # distance covered this tick.s
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        #dx, dy, dz = dx * d, dy * d, dz * d
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt
        # collisions
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)

    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        x, y, z = self.position
        for face in FACES:
              # check all surrounding blocks 
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                if self.sneaking:
                    for dy in xrange(height):  # check each height
                        op = list(np)
                        op[1] -= dy
                        op[i] += face[i]
                        if tuple(op) not in self.model.world:
                            continue
                        p[i] -= (d - pad) * face[i]
                        p[1] -= 0.2
                        if p[1] <= int(p[1]) + 0.5:
                            p[1] = int(p[1]) + 0.55
                        if face == (0, -1, 0) or face == (0, 1, 0):
                            # You are colliding with the ground or ceiling, so stop
                            # falling / rising.
                            self.dy = 0
                        if face != (0, -1, 0):
                            p[1] = int(p[1]) + 0.55
                            if face == (0, 0, 1):
                                print(1)
                                p[2] = int(p[2]) + 0.3
                                if p[2] < int(p[2]) + 0.3:
                                    p[2] = int(p[2]) + 0.3
                                p[1] = int(p[1]) + 0.6
                            if face == (0, 0, -1):
                                print(2)
                                p[2] = int(p[2]) - 0.3
                                if p[2] < int(p[2]) - 0.3:
                                    p[2] = int(p[2]) - 0.3
                                p[1] = int(p[1]) + 0.6
                            if face == (1, 0, 0):
                                print(3)
                                p[0] = int(p[0]) + 0.3
                                if p[0] < int(p[0]) + 0.3:
                                    p[0] = int(p[0]) + 0.3
                                p[1] = int(p[1]) + 0.6
                            if face == (-1, 0, 0):
                                print(4)
                                p[0] = int(p[0]) - 0.3
                                if p[0] < int(p[0]) - 0.3:
                                    p[0] = int(p[0]) - 0.3
                                p[1] = int(p[1]) + 0.6
                        break
                elif self.modus == 3:
                    for dy in xrange(height):  # check each height
                        op = list(np)
                        op[1] -= dy
                        op[i] += face[i]
                        
                else:
                    for dy in xrange(height):  # check each height
                        op = list(np)
                        op[1] -= dy
                        op[i] += face[i]
                        if tuple(op) not in self.model.world:
                            continue
                        p[i] -= (d - pad) * face[i]
                        if face == (0, -1, 0) or face == (0, 1, 0):
                            # You are colliding with the ground or ceiling, so stop
                            # falling / rising.
                            self.dy = 0
                        break
        return tuple(p)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """

        if self.exclusive:
            if self.modus == 1:
                vector = self.get_sight_vector()
                block, previous = self.model.hit_test(self.position, vector)
                if (button == mouse.RIGHT) and self.surv_inv[self.inv * 2 + 1] > 0 or \
                        ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)) and self.surv_inv[self.inv * 2 + 1] > 0:
                    # ON OSX, control + left click = right click.
                    if previous:
                        self.model.add_block(previous, self.block)
                        if self.block in self.surv_inv:
                            i = self.surv_inv.index(self.block)
                            self.surv_inv[i + 1] -= 1
                            print(self.surv_inv[i + 1], i)
                        self.creative_inventory.pop(23)
                        random_block = []
                        x1 = random.randint(0, 31)
                        x2 = random.randint(0, 31)
                        x3 = random.randint(0, 31)
                        y1 = random.randint(13, 31)
                        y2 = random.randint(13, 31)
                        y3 = random.randint(13, 31)
                        random_block = tex_coords((x1, y1), (x2, y2), (x3, y3))
                        self.creative_inventory.insert(23, random_block)
                elif button == pyglet.window.mouse.LEFT and block:
                    texture = self.model.world[block]
                    if texture != BEDROCK and texture != BARRIER:
                        self.model.remove_block(block)
                        if texture in self.surv_inv:
                            i = self.surv_inv.index(texture)
                            self.surv_inv[i + 1] += 1
                            print(self.surv_inv[i + 1], i)


            elif self.modus == 2:
                vector = self.get_sight_vector()
                block, previous = self.model.hit_test(self.position, vector)
                if (button == mouse.RIGHT) or \
                        ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                    # ON OSX, control + left click = right click.
                    if previous:
                        self.model.add_block(previous, self.block)
                        self.creative_inventory.pop(23)
                        random_block = []
                        x1 = random.randint(0, 31)
                        x2 = random.randint(0, 31)
                        x3 = random.randint(0, 31)
                        y1 = random.randint(13, 31)
                        y2 = random.randint(13, 31)
                        y3 = random.randint(13, 31)
                        random_block = tex_coords((x1, y1), (x2, y2), (x3, y3))
                        self.creative_inventory.insert(23, random_block)
                elif button == pyglet.window.mouse.LEFT and block:
                    texture = self.model.world[block]
                    if texture != BEDROCK and texture != BARRIER:
                        self.model.remove_block(block)
            
            
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        if self.exclusive:
            m = 0.15
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.rotation = (x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.modus != 3:
            if scroll_y < 0:
                if self.inv == len(self.creative_inventory):
                    self.inv = 0
                else:
                    self.inv += 1
                if self.inv == len(self.creative_inventory):
                    self.inv = 0
            elif scroll_y > 0:
                if self.inv == 0:
                    self.inv = len(self.creative_inventory) - 1
                else:
                    self.inv -= 1
                if self.inv == 0:
                    self.inv = len(self.creative_inventory) - 1
            self.block = self.creative_inventory[self.inv]


    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        
        if symbol == key.W:
            self.strafe[0] -= 1
        elif symbol == key.S:
            self.strafe[0] += 1
        elif symbol == key.A:
            self.strafe[1] -= 1
        elif symbol == key.D:
            self.strafe[1] += 1
        elif symbol == key.Q:
            self.running = not self.running
        elif symbol == key.LSHIFT:
            self.sneaking = not self.sneaking
        elif symbol == key.SPACE:
            if self.dy == 0:
                self.dy = JUMP_SPEED
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        
        elif symbol == key.TAB and self.modus == 2:
            self.flying = not self.flying

        if symbol == key._1:
            self.modus = 1
            self.flying = False
            print(1)
        if symbol == key._2:
            self.modus = 2
            print(2)
        if symbol == key._3:
            self.modus = 3
            self.flying = True
            print(3)
            

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        
        if symbol == key.W:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.A:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1
        elif symbol == key.Q:
            self.running = not self.running
        elif symbol == key.LSHIFT:
            self.sneaking = not self.sneaking

    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.

        """
        # label
        self.label_1.y = height - 10
        self.label_2.y = height - 70
        self.label_3.y = height - 40

        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        #self.draw_breaking_block()
        self.model.batch.draw()
        self.draw_focused_block()
        self.set_2d()
        self.draw_label()
        self.draw_reticle()

        
    def draw_breaking_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            texture_data = list(BREAK_BLOCK)
            self.model._show[block] = self.batch.add(24, GL_QUADS, self.group,
                ('v3f/static', vertex_data),
                ('t2f/static', texture_data))
            print(99)"""

        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[1]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.03125)
            texture_data = list(BREAK_BLOCK)
            glColor3d(0.5, 0.5, 0.5)
            glPolygonMode(GL_FRONT, GL_FILL)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glColor3d(1, 1, 1)
            glPolygonMode(GL_FRONT, GL_FILL)

            

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        if self.modus != 3:
            vector = self.get_sight_vector()
            block = self.model.hit_test(self.position, vector)[0]
            if block:
                x, y, z = block
                vertex_data = cube_vertices(x, y, z, 0.505)
                glColor3d(0, 0, 0)
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self):
        """ Draw the label in the top left of the screen.

        """
        x, y, z = self.position
        self.label_1.text = '%02d (%.2f, %.2f, %.2f) %d / %d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.model._shown), len(self.model.world))
        self.label_1.draw()

        if self.modus == 1:
            self.label_2.text = '%s, %d' % (
                inventory_names[self.inv], self.surv_inv[self.inv * 2 + 1])
            self.label_2.draw()
        elif self.modus == 2:
            self.label_2.text = inventory_names[self.inv]
            self.label_2.draw()

        self.label_3.text = self.modus_names[self.modus - 1]
        self.label_3.draw()


    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)

    


def setup_fog():
    """ Configure the OpenGL fog properties.

    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def setup():
    """ Basic OpenGL configuration.

    """
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


    
   

def main():
    window = Window(width=800, height=600, caption='PyCraft', resizable=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.maximize()
    window.set_fullscreen(fullscreen=False)
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()

    

if __name__ == '__main__':
    main()
