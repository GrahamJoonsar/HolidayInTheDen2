import pygame 
import math
import time

DEBUG = False

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
font = pygame.font.SysFont('Comic Sans MS', 30)
left_text = font.render("0", True, (255, 255, 255), (0, 0, 0))
left_rect = left_text.get_rect()
left_rect.center = (window_width/4, 20)

right_text = font.render("0", True, (255, 255, 255), (0, 0, 0))
right_rect = right_text.get_rect()
right_rect.center = (3*window_width/4, 20)

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

# Point tracker
left_score = 0
right_score = 0

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
        self.original_image = pygame.transform.scale(image, (185, 185))
        self.flashed_image = self.original_image.copy()
        self.flashed_image.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
        self.image = self.original_image
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
        # self.invisible should NOT be relied upon for checking status
        self.invisible = False
        self.last_invisible = self.invisible

    def update(self, other_players, rect_bars, circ_bars):
        if self.invisible != self.last_invisible:
            if self.invisible:
                self.image = self.flashed_image
            else:
                self.image = self.original_image

        self.last_invisible = self.invisible
        if self.last_thrown < time.time():
            self.invisible = False
        else:
            # achieves flashing effect
            self.invisible = (self.last_thrown - time.time()) % 1 > 0.5

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

        # Barrier Collisions
        for rect in rect_bars:
            if rect.intersects(next_x, self.rect.centery, self.radius):
                next_x = self.rect.centerx
            if rect.intersects(self.rect.centerx, next_y, self.radius):
                next_y = self.rect.centery

        for circ in circ_bars:
            if circ.intersects(next_x, next_y, self.radius):
                angle = math.atan2(next_y - circ.rect.centery, next_x - circ.rect.centerx)
                next_x = circ.rect.centerx + (self.radius + circ.radius)*math.cos(angle)
                next_y = circ.rect.centery + (self.radius + circ.radius)*math.sin(angle)
            
        
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
        global left_score, right_score, left_text, right_text, left_rect, right_rect

        if time.time() - self.last_thrown > 3:
            self.invisible = True
            if self.side == LEFT:
                right_score += 1
                right_text = font.render(str(right_score), True, (255, 255, 255), (0, 0, 0))
                right_rect.center = (3*window_width/4, 20)
            elif self.side == RIGHT:
                left_score += 1
                left_text = font.render(str(left_score), True, (255, 255, 255), (0, 0, 0))
                left_rect.center = (window_width/4, 20)

        self.last_thrown = time.time() + 3


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
        for barrier in rectangle_list:
            if self.check_barriers(barrier):
                self.on_hit()
        for barrier in circle_list:
            if self.check_barriers(barrier):
                self.on_hit()
        if not in_bounds(self.rect.centerx, self.rect.centery, -self.radius, self.side) and not in_bounds(self.rect.centerx, self.rect.centery, -self.radius, RIGHT if self.side==LEFT else LEFT):
            snowball_list.remove(self)
            del self

    def check_collisions(self, player):
        return within(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery, self.radius+player.radius)

    def check_barriers(self, barrier):
        return barrier.intersects(self.rect.centerx, self.rect.centery, self.radius)

    def on_hit(self):
        snowball_list.remove(self)
        del self

class Circle_Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y, r, image):
        # Pygame and image stuff
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (185, 185))
        self.rect = self.image.get_rect()

        self.rect.center = (x, y)
        self.radius = r

    def intersects(self, x_pos, y_pos, radius):
        return within(self.rect.centerx, self.rect.centery, x_pos, y_pos, radius + self.radius)

class Rectangle_Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image):
        # Pygame and image stuff
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (185, 185))
        self.rect = self.image.get_rect()

        self.rect.center = (x, y)
        self.w = w
        self.h = h

    def intersects(self, x_pos, y_pos, radius):
        return (abs(self.rect.centerx - x_pos) < radius + self.w) and (abs(self.rect.centery - y_pos) < radius + self.h)
        
        
# Players
player_img_list = []
for i in range(1, 9):
    player_img_list.append(pygame.transform.rotate(pygame.image.load("imgs/" + str(i) + ".png").convert_alpha(), -90*(2*(i%2)-1)))
player_list = pygame.sprite.Group()

# Snowballs
snowball_img = pygame.image.load("snowball.png").convert_alpha()
snowball_list = pygame.sprite.Group()

# Barriers
wall_img = pygame.image.load("imgs/wall.png").convert_alpha()
tree_img = pygame.image.load("imgs/tree.png").convert_alpha()
igloo_img = pygame.image.load("imgs/igloo.png").convert_alpha()

rectangle_list = pygame.sprite.Group()
rectangle_list.add(Rectangle_Barrier(window_width/3, window_height/2, 15, 67, wall_img))
rectangle_list.add(Rectangle_Barrier(2*window_width/3, window_height/2, 15, 67, wall_img))

circle_list = pygame.sprite.Group()

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

    win.fill((240, 255, 255))
    pygame.draw.line(win, (20, 120, 255), (window_width/2, 0), (window_width/2, window_height))

    if DEBUG:
        for player in player_list:
            pygame.draw.circle(win, (0, 255, 30), (player.rect.centerx, player.rect.centery), player.radius)
        #print("snowball count = " + str(len(snowball_list.sprites())), end=" \r")
    
    player_list.draw(win)
    player_list.update(player_list, rectangle_list, circle_list)
    snowball_list.update(player_list)
    snowball_list.draw(win)
    rectangle_list.draw(win)

    win.blit(left_text, left_rect)
    win.blit(right_text, right_rect)

    pygame.display.update()

pygame.quit()
