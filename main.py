import pygame 
import math
import random

DEBUG = True

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

num_players = 2

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


# Sides for the game
LEFT = 0
RIGHT = 1

def within(x1, y1, x2, y2, dist):
    return (x1-x2)**2 + (y1-y2)**2 <= dist*dist

def in_bounds(x, y, r, side):
    x_check = r + side*window_width/2 <= x and x <= window_width-r - (1-side)*window_width/2
    y_check = r <= y and y <= window_height-r
    return x_check and y_check

# The player class, who throw snowballs
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, side, number, image):
        # Pygame and image stuff
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (75, 75))
        self.rect = self.image.get_rect()

        self.rect.center = (x, y)
        self.color = colors[number]

        # Game stuff
        self.side = side
        self.number = number
        self.x_vel = 0
        self.y_vel = 0
        self.radius = 37

    def update(self, other_players):
        self.x_vel = pygame.joystick.Joystick(self.number).get_axis(0) * 10
        self.y_vel = pygame.joystick.Joystick(self.number).get_axis(1) * 10

        next_x = self.rect.centerx + self.x_vel
        next_y = self.rect.centery + self.y_vel

        # Player Collisions
        #for player in other_players:
            
        
        # Boundary Collisions (Perfect)
        if not in_bounds(next_x, self.rect.centery, self.radius, self.side):
            if self.x_vel < 0:
                next_x = self.radius + self.side*window_width/2
            elif self.x_vel > 0:
                next_x = window_width/2 + self.side*window_width/2 - self.radius
        if not in_bounds(self.rect.centerx, next_y, self.radius, self.side):
            if self.y_vel < 0:
                next_y = self.radius
            elif self.y_vel > 0:
                next_y = window_height - self.radius
        
        self.rect.centerx = next_x
        self.rect.centery = next_y

class Snowball(pygame.sprite.Sprite):
    speed = 1
    radius = 8
    def __init__(self, x, y, side):
        # Pygame and image stuff
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()

        self.rect.center = (x, y)
        self.side = side
        self.enabled = True
    
    def update(self):
        if enabled:
            if self.side == LEFT:
                self.rect.centerx += speed
            else:
                self.rect.centerx -= speed
            for p in player_list:
                if p.side != self.side:
                    if self.check_collisions(p):
                        #p.on_hit()
                        self.on_hit()

    def check_collisions(self, player):
        return within(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery, self.radius+player.radius)

    def on_hit(self):
        self.enabled = False

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

player_img = pygame.image.load("player.png").convert_alpha()
player_list = pygame.sprite.Group()

# Generating the players
for i in range(num_players):
    x = window_width/2 + ((i%2)*2-1)*window_width/4
    y = window_height/(num_players+2) * (i+1)
    player_list.add(Player(x, y, 0, i, player_img))

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

    if DEBUG:
        for player in player_list:
            pygame.draw.circle(win, (0, 255, 30), (player.rect.centerx, player.rect.centery), player.radius)
    
    player_list.draw(win)
    player_list.update(player_list)

    pygame.display.update()

pygame.quit()
