import pygame 
import math
import random

# Window Setup
""" THESE DIMENSIONS MIGHT NEED TO BE CHANGED """
window_width = 1366
window_height = 768

# Initializing pygame, and the window
pygame.init()
win = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Snowball Fight!")

# Initializing the font, we may have to change the font size
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 30)

num_players = 8

# Initializing the joysticks, there should be 8 for 8 players
pygame.joystick.init()
if pygame.joystick.get_count() != num_players:
    print("ERROR: Incorrect number of joysticks")
    print("There are only " + str(pygame.joystick.get_count()) + " joysticks.")

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# List of 8 unique and distinct colors, good for identifying the players
colors = [(255, 0, 0, 255), 
          (0, 255, 0, 255),
          (0, 0, 255, 255), 
          (255, 255, 0, 255), 
          (255, 0, 255, 255), 
          (0, 255, 255, 255), 
          (255, 100, 100, 255), 
          (165, 42, 42, 255)
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, side, number, img):
        # Pygame and image stuff
        pygame.sprite.Sprite.__init__(self)

        # Positional and game stuff
        self.x = x
        self.y = y
        self.side = side
        self.number = number

class Snowball(pygame.sprite.Sprite):
    def __init__(self, x, y, side):
        self.x = x
        self.y = y
        self.side = side

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

# Main Loop (Press ESC to force quit)
running = True
while running:
    # Event processing
    pygame.time.delay(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    win.fill((140, 140, 255))

    pygame.display.update()

pygame.quit()
