import pygame
import math
import random
import copy


# Data inside classes(for convenience)
class Game_var:
    w = 600
    h = 600
    land_height_max = 400 # from top
    land_height_min = 550 # from top
    gravity = .5
    landres = 30 #ammount of land points

    keypress_move_distance = 2 
    keypress_angle = 2 #in degrees

class Colors:
    background = (15, 15, 60)
    blue1 = (20, 150, 255)
    red1 = (255, 50, 0)
    grey = (110, 100, 130)
    gray_r = (150, 230, 80)

# Init
pygame.init()
pygame.display.set_caption("Lunar Lander")
screen = pygame.display.set_mode([Game_var.w, Game_var.h])

# Classes
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_coliding = False

    # Return a list
    def returnl(self):
        return (self.x, self.y)

    # not needed
    def distance_point(self, point):
        return math.sqrt((abs (point.x - self.x))**2 + (abs(point.y - self.y))**2)
        #TODO delete pass upon wtiting something here

    def distance_line():
        #TODO delete pass upon wtiting something here
        pass

    def rotate_vector(self, angle):
        # https://en.wikipedia.org/wiki/Rotation_matrix
        x = self.x
        y = self.y
        self.x = (x * math.cos(math.radians(angle)) - y * math.sin(math.radians(angle)))
        self.y = (y * math.cos(math.radians(angle)) + x * math.sin(math.radians(angle)))
    
    # used for collisions
    def line_point_get_Y(self, line_p1, line_p2):
        # y = k*x + q
        k = (line_p2.y - line_p1.y) / (line_p2.x - line_p1.x)
        q = line_p1.y - k * line_p1.x
        return (k * self.x + q)
    
class Rocket:
    position = Point(0, 0)
    image = ""
    def_points =  [Point(0, -20), Point(15, -5), Point(20, 25), Point(-20, 25), Point(-15, -5)] #defined at angle 0, relative to the center of rotation defined by x and y
    col_points = list()

    def __init__(self, x, y):
        self.position = Point(x, y)
        self.angle = 0

        for i in self.def_points:
            self.col_points.append(Point(i.x + self.position.x, i.y + self.position.y))
        
        self.is_coliding = False

    def movex(self, plusx):
        self.position.x += plusx
        for i in self.col_points:
            i.x += plusx

    def movey(self, plusy):
        self.position.y += plusy
        for i in self.col_points:
            i.y += plusy
        
    def rotate(self, angle):
        # do not use the col_points for this, it will slowly deform
        self.angle = (self.angle + angle) % 360

        # https://en.wikipedia.org/wiki/Rotation_matrix
        temp = copy.deepcopy(self.def_points) # deepcopy necessary

        points = list()
        for i in temp:
            i.rotate_vector(self.angle)
            points.append(Point(i.x + self.position.x, i.y + self.position.y))

        self.col_points = list(points)

    def fly(self):
        # TODO delete pass upon wtiting something here
        # use movex and movey to simplify, move based on angle
        pass

    def col_check_l(self, land):
        # TODO
        self.is_coliding = False

        # loop through land points 
        for i in self.col_points:
            closest_left_index = 0
            for j in range(len(land.land)):
                #TODO
                if land.land[j].x < i.x:
                    closest_left_index = j


            if (i.line_point_get_Y(land.land[closest_left_index - 1], land.land[closest_left_index]) - i.y < 0):
                self.is_coliding = True

    def returnl(self):
        return self.position.returnl()

    def draw(self):
        temp = list()
        for i in self.col_points:
            temp.append(i.returnl())
        pygame.draw.polygon(screen, Colors.gray_r, temp)


class Land:
    def __init__(self):
        self.land = list()
        self.land_print = list()
        self.landplace = list()

    def generate(self):
        self.land.clear()
        self.land.append(Point(0, random.randint(Game_var.land_height_max, Game_var.land_height_min))) #first point
        for i in range(Game_var.landres):
            self.land.append(Point(int(Game_var.w / (Game_var.landres+1)) * (i+1), random.randint(Game_var.land_height_max, Game_var.land_height_min)))
        self.land.append(Point(Game_var.w, random.randint(Game_var.land_height_max, Game_var.land_height_min))) #last point
        # bottom corners
        self.land.append(Point(Game_var.w, Game_var.h))
        self.land.append(Point(0, Game_var.h))

        # landing place
        lp1 = random.randint(0, (Game_var.landres))
        self.land[lp1 + 1].y = self.land[lp1].y


        # load into second list, which uses no Points
        for i in self.land:
            self.land_print.append(i.returnl())

    def draw(self):
        pygame.draw.polygon(screen, Colors.grey, self.land_print)

    def clear(self):
        self.land.clear()

class Background:
    def __init__(self):
        #TODO delete pass upon wtiting something here
        pass

###########################

l1 = Land()
l1.generate()

# Game loop
running = True
rocket = Rocket(150, 120)
rocket.rotate(90)

while running:

    #TODO start menu, end menu, if statement, int state? 0-menu 1-game 2-end

    # Inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Controls
    #TODO manage key release, acceleration support, gravity
    if pygame.key.get_pressed()[pygame.K_w]:
        rocket.movey(-Game_var.keypress_move_distance)
    if pygame.key.get_pressed()[pygame.K_s]:
        rocket.movey(Game_var.keypress_move_distance)
    if pygame.key.get_pressed()[pygame.K_a]:
        rocket.movex(-Game_var.keypress_move_distance)
    if pygame.key.get_pressed()[pygame.K_d]:
        rocket.movex(Game_var.keypress_move_distance)

    if pygame.key.get_pressed()[pygame.K_h]:
        rocket.rotate(-Game_var.keypress_angle)
    if pygame.key.get_pressed()[pygame.K_l]:
        rocket.rotate(Game_var.keypress_angle)


    screen.fill(Colors.background)

    l1.draw()

    # DO NOT DELETE THE CIRCLE, it is for reference in case the rocket gets broken it is easier to notice
    # also will be used as a collision indicator for testing purposes
    rocket.col_check_l(l1)
    if rocket.is_coliding:
        pygame.draw.circle(screen, Colors.red1, rocket.returnl(), 50, 4)
    else:
        pygame.draw.circle(screen, Colors.blue1, rocket.returnl(), 60, 2)

    rocket.draw()
    
    pygame.display.flip()

    #fps limit, should be fine
    pygame.time.Clock().tick(60)

# Quit
pygame.quit()
