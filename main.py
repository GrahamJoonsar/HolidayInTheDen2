import pygame 
import math
import time

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

num_players = 8
throwing_cooldown = 1

# Initializing the joysticks, there should be 8 for 8 players
pygame.joystick.init()
if pygame.joystick.get_count() != num_players and not DEBUG:
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
    return (x1-x2)**2 + (y1-y2)**2 < dist*dist

def in_bounds(x, y, r, side):
    x_check = r + side*window_width/2 <= x and x <= window_width-r - (1-side)*window_width/2
    y_check = r <= y and y <= window_height-r
    return x_check and y_check

# The player class, who throw snowballs
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, side, number, image):
        # Pygame and image stuff
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (185, 185))
        self.rect = self.image.get_rect()

        self.rect.center = (x, y)
        self.color = colors[number]

        # Game stuff
        self.side = side
        self.number = number
        self.x_vel = 0
        self.y_vel = 0
        self.radius = 30
        self.last_thrown = 0

    def update(self, other_players):
        self.x_vel = pygame.joystick.Joystick(self.number).get_axis(0) * 10
        self.y_vel = pygame.joystick.Joystick(self.number).get_axis(1) * 10
        if pygame.joystick.Joystick(self.number).get_button(2) and self.last_thrown + throwing_cooldown < time.time():
            self.last_thrown = time.time()
            snowball_list.add(Snowball(self.rect.centerx, self.rect.centery, self.side, snowball_img))

        next_x = self.rect.centerx + self.x_vel
        next_y = self.rect.centery + self.y_vel

        # Player Collisions
        for other in other_players:
            if within(next_x, next_y, other.rect.centerx, other.rect.centery, self.radius + other.radius) and other.number != self.number:
                angle = math.atan2(next_y - other.rect.centery, next_x - other.rect.centerx)
                next_x = other.rect.centerx + (self.radius + other.radius)*math.cos(angle)
                next_y = other.rect.centery + (self.radius + other.radius)*math.sin(angle)
        
        # Boundary Collisions (Perfect)
        if not in_bounds(next_x, self.rect.centery, self.radius, self.side):
            if next_x - self.rect.centerx < 0:
                next_x = self.radius + self.side*window_width/2
            elif next_x - self.rect.centerx > 0:
                next_x = window_width/2 + self.side*window_width/2 - self.radius
        if not in_bounds(self.rect.centerx, next_y, self.radius, self.side):
            if next_y - self.rect.centery < 0:
                next_y = self.radius
            elif next_y - self.rect.centery > 0:
                next_y = window_height - self.radius
        
        self.rect.centerx = next_x
        self.rect.centery = next_y

    def on_hit(self):
        return

class Snowball(pygame.sprite.Sprite):
    speed = 10
    radius = 8
    def __init__(self, x, y, side, img):
        # Pygame and image stuff
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(img, (75, 75))
        self.rect = self.image.get_rect()

        self.rect.center = (x, y)
        self.side = side
        self.enabled = True
    
    def update(self, players):
        if self.side == LEFT:
            self.rect.centerx += self.speed
        else:
            self.rect.centerx -= self.speed
        for p in players:
            if p.side != self.side:
                if self.check_collisions(p):
                    p.on_hit()
                    self.on_hit()
        if not in_bounds(self.rect.centerx, self.rect.centery, -self.radius, self.side) and not in_bounds(self.rect.centerx, self.rect.centery, -self.radius, RIGHT if self.side==LEFT else LEFT):
            snowball_list.remove(self)
            del self

    def check_collisions(self, player):
        return within(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery, self.radius+player.radius)

    def on_hit(self):
        snowball_list.remove(self)
        del self

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

player_img_list = []
for i in range(1, 9):
    player_img_list.append(pygame.transform.rotate(pygame.image.load("imgs/" + str(i) + ".png").convert_alpha(), -90*(2*(i%2)-1)))
player_list = pygame.sprite.Group()
snowball_img = pygame.image.load("snowball.png").convert_alpha()
snowball_list = pygame.sprite.Group()

# Generating the players
for i in range(num_players):
    x = window_width/2 + ((i%2)*2-1)*window_width/4
    y = window_height/(num_players+2) * (i+1)
    player_list.add(Player(x, y, i%2, 0 if DEBUG else i, player_img_list[i]))

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
        print("snowball count = " + str(len(snowball_list.sprites())), end=" \r")
    
    player_list.draw(win)
    player_list.update(player_list)
    snowball_list.update(player_list)
    snowball_list.draw(win)

    pygame.display.update()

pygame.quit()
