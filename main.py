import numpy as np
import pygame as pg
from random import randint

pg.init()
pg.font.init()
all_sprites = pg.sprite.Group()

# The description of colors

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

SCREEN_SIZE = (800, 600)


# This function randomly generates color
def rand_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


class Ball:
    """
    The ball class. Creates a two types of ball, controls it's movement and
    implement it's rendering.
    """

    def __init__(self, coord, vel, rad=20, color=None, width=None):
        """
        Constructor method. Initializes ball's parameters and initial values.
        """
        self.coord = coord
        self.vel = vel
        if color is None:
            color = rand_color()
        self.color = color
        self.rad = rad
        if width is None:
            width = randint(0, 1)
        self.width = width
        self.is_alive = True

    def check_corners(self, refl_ort=0.8, refl_par=0.9):
        """
        Reflects ball's velocity when ball bumps into the screen corners.
        Implemetns inelastic rebounce.
        """
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)

    def move(self, time=1, grav=3):
        """
        Moves the ball according to it's velocity and time step.
        Changes the ball's velocity due to gravitational force.
        """
        self.vel[1] += grav
        for i in range(2):
            self.coord[i] += time * self.vel[i]
        self.check_corners()
        if self.vel[0] ** 2 + self.vel[1] ** 2 < 2 ** 2 and self.coord[1] > \
                SCREEN_SIZE[1] - 2 * self.rad:
            self.is_alive = False

    def draw(self, screen):
        """
        Draws the ball on appropriate surface.
        """
        pg.draw.circle(screen, self.color, self.coord, self.rad, self.width)


class Target:
    """
    Target class. Creates target, manages it's rendering and collision with a
    ball event.
    """

    def __init__(self, coord=None, color=None, rad=30, width=0):
        """
        Constructor method. Sets coordinate, color and radius of the target.
        """
        if coord is None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad),
                     randint(rad, SCREEN_SIZE[1] - rad)]
        self.coord = coord
        self.rad = rad
        self.width = width

        if color is None:
            color = rand_color()
        self.color = color

    def check_collision(self, ball):
        """
        Checks whether the ball bumps into target.
        """
        dist = sum(
            [(self.coord[i] - ball.coord[i]) ** 2 for i in range(2)]) ** 0.5
        min_dist = self.rad + ball.rad
        return dist <= min_dist

    def draw(self, screen):
        """
        Draws the target on the screen
        """
        pg.draw.circle(screen, self.color, self.coord, self.rad, self.width)

    def move(self):

        pass


class MovingTarget(Target):
    """
    moving target class, manges moving of a target
    """

    def __init__(self, coord=None, color=None, rad=30, width=0):
        """
        Constructor method. Sets coordinate, color, radius
         Ox and Oy speed of the target.
        :param coord:
        :param color:
        :param rad:
        """
        super().__init__(coord, color, rad)
        self.vx = randint(-2, +2)
        self.vy = randint(-2, +2)
        if width == 0:
            self.width = 5

    def wall_collision(self):
        """
        Maneges collisions with walls
        :return:
        """
        if 30 > self.coord[0] or SCREEN_SIZE[0] - 30 < self.coord[0]:
            self.vx = -self.vx
        if 30 > self.coord[1] or SCREEN_SIZE[1] - 30 < self.coord[1]:
            self.vy = -self.vy

    def move(self):
        """
        Maneges moving of a target
        :return:
        """
        self.wall_collision()
        self.coord[0] += self.vx
        self.coord[1] += self.vy


class TankSprite(pg.sprite.Sprite):
    """
    This class maneges work of a tank sprite
    """
    def __init__(self, team_color):
        pg.sprite.Sprite.__init__(self)
        self.color = team_color
        if self.color == RED:
            self.image = Tpic
        elif self.color == WHITE:
            self.image = Tpic1
        self.rect = self.image.get_rect()
        self.rect.center = (30, 30)

    def update(self, xcor, ycor):
        self.rect.x = xcor - 70
        self.rect.y = ycor - 30


class Gun:
    """
    Gun class. Manages it's renderring, movement and striking.
    """
    def __init__(self, team_color,
                 min_pow=20, max_pow=50):
        self.color = team_color
        self.coord = [30, SCREEN_SIZE[1] // 2]
        if self.color == WHITE:
            self.coord[0] = 770
        self.angle = 0
        self.min_pow = min_pow
        self.max_pow = max_pow
        self.power = min_pow
        self.active = False
        self.alive = True
        self.sprite = TankSprite(self.color)
        self.radius = 30

    def hit_target(self, hit_coord):
        if ((hit_coord[0] - self.coord[0]) ** 2 + (hit_coord[1] -
                                                   self.coord[1]) ** 2
                <= (self.radius + 15) ** 2):
            self.coord = [30, SCREEN_SIZE[1] // 2]
            if self.color == WHITE:
                self.coord[0] = 770
            return 1
        else:
            return 0

    def draw(self, screen):
        end_pos = [self.coord[0] + self.power * np.cos(self.angle),
                   self.coord[1] + self.power * np.sin(self.angle)]
        pg.draw.line(screen, self.color, self.coord, end_pos, 5)
        self.sprite.update(self.coord[0], self.coord[1])

    def strike(self):
        vel = [int(self.power * np.cos(self.angle)),
               int(self.power * np.sin(self.angle))]
        self.active = False
        self.power = self.min_pow
        return Ball(list(self.coord), vel)

    def move(self):
        if self.active and self.power < self.max_pow:
            self.power += 1

    def set_angle(self, mouse_pos):
        self.angle = np.arctan2(mouse_pos[1] - self.coord[1],
                                mouse_pos[0] - self.coord[0])


class ScoreTable:
    """
    Score table class.
    """

    def __init__(self, t_destr=0, b_used=0):
        self.t_destr = t_destr
        self.b_used = b_used
        self.font = pg.font.SysFont("dejavusansmono", 25)

    def score(self):
        """
        Score calculation method.
        """
        return self.t_destr - self.b_used

    def draw(self, screen):
        score_surf = [
            self.font.render("Destroyed: {}".format(self.t_destr), True, WHITE),
            self.font.render("Balls used: {}".format(self.b_used), True, WHITE),
            self.font.render("Total: {}".format(self.score()), True, RED)]
        for i in range(3):
            screen.blit(score_surf[i], [10, 10 + 30 * i])


class Manager:
    """
    Class that manages events' handling, ball's motion and collision, target
    creation, etc.
    """

    def __init__(self, n_targets=1):
        self.balls = []
        self.guns = [Gun(RED), Gun(WHITE)]
        self.targets = []
        self.score_t = ScoreTable()
        self.n_targets = n_targets
        self.new_mission()

    def new_mission(self):
        """
        Adds new targets.
        """
        for i in range(self.n_targets):
            self.targets.append(Target(rad=randint(
                max(1, 30 - 2 * max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
        for i in range(self.n_targets):
            self.targets.append(MovingTarget(rad=randint(
                max(1, 30 - 2 * max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))

    def process(self, events, screen):
        """
        Runs all necessary method for each iteration. Adds new targets, if
        previous are destroyed.
        """
        done = self.handle_events(events)
        self.move()
        self.collide()
        self.draw(screen)

        if len(self.targets) == 0 and len(self.balls) == 0:
            self.new_mission()

        return done

    def handle_events(self, events):
        """
        Handles events from keyboard, mouse, etc.
        """
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.guns[1].coord[1] -= 20
                elif event.key == pg.K_DOWN:
                    self.guns[1].coord[1] += 20
                elif event.key == pg.K_LEFT:
                    self.guns[1].coord[0] -= 20
                elif event.key == pg.K_RIGHT:
                    self.guns[1].coord[0] += 20
                if event.key == pg.K_w:
                    self.guns[0].coord[1] -= 20
                elif event.key == pg.K_s:
                    self.guns[0].coord[1] += 20
                elif event.key == pg.K_a:
                    self.guns[0].coord[0] -= 20
                elif event.key == pg.K_d:
                    self.guns[0].coord[0] += 20
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.guns[0].active = True
                if event.button == 3:
                    self.guns[1].active = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.guns[0].strike())
                    self.score_t.b_used += 1
                if event.button == 3:
                    self.balls.append(self.guns[1].strike())
                    self.score_t.b_used += 1
        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            for gun in self.guns:
                gun.set_angle(mouse_pos)

        return done

    def draw(self, screen):
        """
        Runs balls', gun's, targets' and score table's drawing method.
        """
        for ball in self.balls:
            ball.draw(screen)
        for target in self.targets:
            target.draw(screen)
        all_sprites.draw(screen)
        for gun in self.guns:
            gun.draw(screen)
        self.score_t.draw(screen)

    def move(self):
        """
        Runs balls' and gun's movement method, removes dead balls.
        """
        dead_balls = []
        for i, ball in enumerate(self.balls):
            ball.move()
            if not ball.is_alive:
                dead_balls.append(i)
        for i in reversed(dead_balls):
            self.balls.pop(i)
        for i, target in enumerate(self.targets):
            target.move()
        for gun in self.guns:
            gun.move()

    def collide(self):
        """
        Checks whether balls bump into targets, sets balls' alive trigger.
        """
        collisions = []
        targets_c = []
        for i, ball in enumerate(self.balls):
            for j, target in enumerate(self.targets):
                if target.check_collision(ball):
                    collisions.append([i, j])
                    targets_c.append(j)
        targets_c.sort()
        for j in reversed(targets_c):
            self.score_t.t_destr += 1
            self.targets.pop(j)


screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("Пушка")
Tpic = pg.image.load('T90pic.png').convert()
Tpic1 = pg.image.load('T90pic1.png').convert()

done = False
clock = pg.time.Clock()

mgr = Manager(n_targets=3)
all_sprites.add(mgr.guns[0].sprite, mgr.guns[1].sprite)

while not done:
    clock.tick(15)
    screen.fill(BLACK)

    done = mgr.process(pg.event.get(), screen)

    pg.display.flip()

pg.quit()
