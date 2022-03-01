import pygame

WINDOW_SIZE = WIDTH, HEIGHT = 640, 512
LEVELS_DIR = 'level_maps'
TILE_SIZES = {'close': 64, 'further': 32}
SPRITES_INCREASE = 2
DATA_DIR = 'data'
SPRITES_SKIN_DIR = 'sprites'
SOUNDS_BACKGROUNDS_DIR = 'other'
INFO_ABOUT_LEVELS_FILE_NAME = 'LevelsInformation.json'
BULLET_SIZE = 40
GRAVITY = 0.3
SCREEN_RECT = (0, 0, WIDTH, HEIGHT)
ANIMATION_EVENTTYPE = pygame.USEREVENT + 1
FIRINGBULLET_EVENTTYPE = pygame.USEREVENT + 2
FPS = 60
COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)
LEVELS_NAMES = ["UndergrounD", "DinosauR", "TurtlE"]