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

    g = .01

    landres = 20 #ammount of ground points 
    land_point_max = 3 # maximum ammount of landing points

    rocket_init_fuel = 700
    rocket_fly_fuel_consumption = 1
    rocket_rotate_fuel_consumption = .1
    rocket_land_tolerance_angle = 10
    rocket_land_max_speed = .5

    keypress_move_distance = 4 
    keypress_angle = 2 #in degrees

class Colors:
    background = (15, 15, 60)
    white1 = (255, 250, 220)
    cyan1 = (120, 210, 255)
    blue1 = (20, 150, 255)
    red1 = (255, 50, 0)
    grey1 = (110, 100, 130)
    green1 = (150, 230, 80)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_coliding = False

    # Return a list
    def returnl(self):
        return (self.x, self.y)

    # not needed
    def size(self):
        return math.sqrt(self.x**2 + self.y**2)

    def rotate_vector(self, angle):
        # https://en.wikipedia.org/wiki/Rotation_matrix
        x = self.x
        y = self.y
        self.x = (x * math.cos(math.radians(angle)) - y * math.sin(math.radians(angle)))
        self.y = (y * math.cos(math.radians(angle)) + x * math.sin(math.radians(angle)))
    
    # used for collisions
    def line_point_get_Y(self, line_p1, line_p2):
        # y = k*x + q
        if line_p2.x == line_p1.x:
            return self.y
        k = (line_p2.y - line_p1.y) / (line_p2.x - line_p1.x)
        q = line_p1.y - k * line_p1.x
        return (k * self.x + q)

    def line_point_get_point(self, line_p1, line_p2):
        # y = k*x + q
        if line_p2.x == line_p1.x:
            return Point(self.x, self.y)
        k = (line_p2.y - line_p1.y) / (line_p2.x - line_p1.x)
        q = line_p1.y - k * line_p1.x

        projectionY = k * self.x + q
        return Point(self.x, projectionY)
    
class Rocket:
    position = Point(0, 0)
    #image = ""
                   #rocket tip
    def_points =  [Point(0, -17), \
            Point(5, -11), Point(9.5, -1), Point(8, 12), \
            Point(-8, 12), Point(-9.5, -1), Point(-5, -11)] #defined at angle 0, relative to the center of rotation defined by x and y
    col_points = list()

    #TODO FIRE

    def __init__(self, x, y):
        self.position = Point(x, y)
        self.angle = 0
        self.velocity = Point(0, 0)
        self.force = Game_var.g * 2.1
        self.fuel = Game_var.rocket_init_fuel
        self.acceleration = Point(0, 0)

        for i in self.def_points:
            self.col_points.append(Point(i.x + self.position.x, i.y + self.position.y))
        
        self.is_coliding = False
        self.is_landing = False
        self.landed = False

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
        self.fuel -= Game_var.rocket_rotate_fuel_consumption

        # https://en.wikipedia.org/wiki/Rotation_matrix
        temp = copy.deepcopy(self.def_points) # deepcopy necessary

        points = list()
        for i in temp:
            i.rotate_vector(self.angle)
            points.append(Point(i.x + self.position.x, i.y + self.position.y))

        self.col_points = list(points)

    def fly(self):
        self.fuel -= Game_var.rocket_fly_fuel_consumption
        up = Point(0 , -1) # ah yes, reversed y
        up.rotate_vector(self.angle)
        self.velocity.x += up.x * self.force
        self.velocity.y += up.y * self.force

    def fall(self):
        self.velocity.y += Game_var.g

    def apply_vel(self):
        self.movex(self.velocity.x)
        self.movey(self.velocity.y)

    def annulvel(self):
        self.velocity = Point(0, 0)

    def angle_land(self):
        self.angle = 0
        self.rotate(0)

    def speed(self):
        return self.velocity.size()

    def fuel_check(self, num):
        return self.fuel > num

    def border_check(self):
        for i in self.col_points:
            if i.x < 0:
                d = i.x - 0
                self.movex(-d)
            if i.x > Game_var.w:
                d = i.x - Game_var.w
                self.movex(-d)
            if i.y < 0:
                d = i.y - 0
                self.movey(-d)
            if i.y > Game_var.h:
                d = i.y - Game_var.h
                self.movey(-d)

    def col_check(self, land):
        self.is_coliding = False
        self.is_landing = False

        # hitbox points against ground
        if self.is_coliding == False:
            for i in self.col_points:
                closest_index = 0
                for j in range(len(land.land) - 2): # -2 is removing polugon points unneccessary for calculations
                                                    # they also break it
                    if (float(i.x) > land.land[j].x):
                        closest_index += 1

                if (i.y > i.line_point_get_Y(land.land[closest_index], land.land[closest_index - 1])):
                    self.is_coliding = True

        # hitbox aginst ground points
        if self.is_coliding == False:
            left_r_hbox_index = 0
            right_r_hbox_index = 0
            for i in range(len(self.col_points)):
                if (self.col_points[i].x < self.col_points[left_r_hbox_index].x):
                    left_r_hbox_index = i
                if (self.col_points[i].x > self.col_points[right_r_hbox_index].x):
                    right_r_hbox_index = i

            for i in land.land:
                # only checks points on the interval between rocket's most left and most right points
                if (i.x > self.col_points[left_r_hbox_index].x and i.x < self.col_points[right_r_hbox_index].x):
                    for j in range(len(self.col_points)):
                        nextp = j + 1
                        if nextp > len(self.col_points) - 1:
                            nextp = 0

                        point_on_line = i.line_point_get_point(self.col_points[j], self.col_points[nextp])#gets a point projection onto a line

                        #checks, whether it is on desired interval and whether it is above the line
                        if (point_on_line.x > self.col_points[j].x and point_on_line.x < self.col_points[nextp].x) \
                                or (point_on_line.x < self.col_points[j].x and point_on_line.x > self.col_points[nextp].x):
                            if (point_on_line.y > i.y):
                                self.is_coliding = True

        # landing
        lowest1_index = 0
        lowest2_index = 0
        for i in range(len(self.col_points)):
            if self.col_points[i].y > self.col_points[lowest1_index].y:
                lowest1_index = i
        if lowest1_index == 0:
            lowest2_index = 1
        for i in range(len(self.col_points)):
            if self.col_points[i].y > self.col_points[lowest2_index].y:
                if i == lowest1_index:
                    continue
                lowest2_index = i

        for i in land.land_points:
            if self.col_points[lowest1_index].x > i.pos.x \
                    and self.col_points[lowest1_index].x < i.pos.x + i.length \
                    and self.col_points[lowest2_index].x > i.pos.x \
                    and self.col_points[lowest2_index].x < i.pos.x + i.length \
                    and (self.angle < Game_var.rocket_land_tolerance_angle or self.angle > 360 - Game_var.rocket_land_tolerance_angle) \
                    and self.speed() < Game_var.rocket_land_max_speed:
                        # print("rocket over landing point")
                        if self.col_points[lowest1_index].y > i.pos.y:
                            self.movey(i.pos.y - self.col_points[lowest1_index].y)
                            self.is_landing = True
                            self.is_coliding = False

    def returnl(self):
        return self.position.returnl()

    def draw(self):
        temp = list()
        for i in self.col_points:
            temp.append(i.returnl())
        pygame.draw.polygon(screen, Colors.green1, temp)

    def draw_data(self):
        font = pygame.font.SysFont('arial', 12)
        pos = "Position: {x:.4f},{y:.4f}".format(x = self.position.x, y = (Game_var.h - self.position.y))
        ang = "Angle:    {angle:.2f} deg".format(angle = self.angle)
        vel = "Velocity: {x:.4f},{y:.4f}".format(x = self.velocity.x, y = self.velocity.y)
        spd = "Speed:    {sp:.4f}".format(sp = self.speed())
        ful = "Fuel:     {fl:.4f}".format(fl = self.fuel)
        screen.blit(font.render(pos, False, Colors.white1), (5, 5))
        screen.blit(font.render(ang, False, Colors.white1), (5, 5 + 12))
        screen.blit(font.render(vel, False, Colors.white1), (5, 5 + 2*12))
        screen.blit(font.render(spd, False, Colors.white1), (5, 5 + 3*12))
        screen.blit(font.render(ful, False, Colors.white1), (5, 5 + 4*12))

class Indicator:
    def __init__(self):
        pass

    def draw(self, rocket):
        if rocket.is_coliding: 
            pygame.draw.circle(screen, Colors.red1, rocket.returnl(), 50, 4)
        elif rocket.is_landing:
            pygame.draw.circle(screen, Colors.green1, rocket.returnl(), 50, 3)
        else:
            pygame.draw.circle(screen, Colors.blue1, rocket.returnl(), 60, 2)

class Land_Point:
    color = Colors.cyan1
    height = 4

    def __init__(self, position, length):
        self.length = length
        self.pos = Point(position.x, position.y - 1)

    def draw(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.pos.x, self.pos.y, self.length, self.height))

class Land:
    def __init__(self):
        self.land = list()
        self.land_print = list()
        self.land_points = list()

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
        place_count = random.randint(1, Game_var.land_point_max)
        #print("places:", place_count)
        temp_count = 0
        taken = list()
        while temp_count < place_count :
            lp_len = random.randint(1,3)
            lp_index = random.randint(0, (Game_var.landres - lp_len))

            def create_land_point(Id, Len):
                for i in range(Len + 1):
                    self.land[Id + i].y = self.land[Id].y
                    taken.append(Id + i)
                self.land_points.append(Land_Point(Point(self.land[Id].x, self.land[Id].y), self.land[Id + Len].x - self.land[Id].x))

            #print("c:", temp_count,"id:", lp_index, " len:", lp_len, " land:", len(self.land))

            compatible = True
            spacing = 1
            for i in range(lp_len + 1 + spacing):
                for j in taken:
                    if lp_index + i - 1 == j:
                        compatible = False

            if compatible:
                create_land_point(lp_index, lp_len)
                temp_count += 1

        # load into second list, which uses no Points
        for i in self.land:
            self.land_print.append(i.returnl())

    def draw(self):
        pygame.draw.polygon(screen, Colors.grey1, self.land_print)
        for i in self.land_points:
            i.draw()

    def clear(self):
        self.land.clear()

class Background:
    def __init__(self, color):
        self.color = color

    def set_bg(self, color):
        self.color = color

    def draw_bg(self):
        screen.fill(self.color)

###########################

# Init
pygame.init()
pygame.display.set_caption("Lunar Lander")
screen = pygame.display.set_mode([Game_var.w, Game_var.h])
l1 = Land()
l1.generate()
bg = Background(Colors.background)
indicator = Indicator()

# Game loop
running = True
lockkeys = False
rocket = Rocket(150, 120)

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
    testing = False
    if pygame.key.get_pressed()[pygame.K_w]:
        rocket.movey(-Game_var.keypress_move_distance)
        testing = True
    if pygame.key.get_pressed()[pygame.K_s]:
        rocket.movey(Game_var.keypress_move_distance)
        testing = True
    if pygame.key.get_pressed()[pygame.K_a]:
        rocket.movex(-Game_var.keypress_move_distance)
        testing = True
    if pygame.key.get_pressed()[pygame.K_d]:
        rocket.movex(Game_var.keypress_move_distance)
        testing = True

    if testing:
        rocket.annulvel()
        rocket.landed = False
        lockkeys = False

    if not testing:
        rocket.fall()

    if not lockkeys:
        # vim keybindings for now
        if pygame.key.get_pressed()[pygame.K_h]:
            if rocket.fuel_check(Game_var.rocket_rotate_fuel_consumption):
                rocket.rotate(-Game_var.keypress_angle)
        if pygame.key.get_pressed()[pygame.K_l]:
            if rocket.fuel_check(Game_var.rocket_rotate_fuel_consumption):
                rocket.rotate(Game_var.keypress_angle)
        if pygame.key.get_pressed()[pygame.K_k]:
            if rocket.fuel_check(Game_var.rocket_fly_fuel_consumption):
                rocket.fly()

    rocket.apply_vel()

    # DO NOT DELETE THE CIRCLE, it is for reference in case the rocket gets broken it is easier to notice
    # also will be used as a collision indicator for testing purposes
    rocket.border_check()
    rocket.col_check(l1)

    if rocket.is_coliding:
        rocket.annulvel()
        lockkeys = True
    elif rocket.is_landing:
        if not rocket.landed:
            rocket.angle_land()
        rocket.annulvel()
        if rocket.angle == 0:
            rocket.landed = True
            lockkeys = True

    # drawing
    bg.draw_bg()
    l1.draw()
    indicator.draw(rocket)

    rocket.draw()
    rocket.draw_data()
    
    pygame.display.flip()

    #fps limit, should be fine
    pygame.time.Clock().tick(60)

# Quit
pygame.quit()
