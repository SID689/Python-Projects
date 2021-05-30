#Game options/settings

TITLE = "JUNGLE JUMP!"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'Comic Sans MS'
HS_FILE = "highscore.txt"
SPRITESHEET = "JPS.png"


#Player Properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20

#Game properties
BOOST_POWER = 60
POW_SPAWN_RATE = 2
MOB_FREQ = 5000
PLAYER_LAYER = 1
PLATFORM_LAYER = 2
POW_LAYER = 1
MOB_LAYER = 2

#Starting Platforms
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT-350),
                 (350, 200),
                 (175, 100)]

#Define Colors
white = (255, 255, 255)
brown = (160, 82, 45)
black = (0, 0, 0)
red = (255, 0, 0)
green = (34, 139, 34)
blue = (0, 0, 255)
whitish = (250, 243, 235)
