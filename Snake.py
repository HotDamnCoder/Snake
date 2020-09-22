import sys
from random import randint
import pygame
from enum import Enum
from collections import deque
from copy import deepcopy


def is_collision(obj: pygame.Rect, obj1: pygame.Rect):
    collision_x = True if obj1.x < obj.x < obj1.x + obj1.width or obj1.x < obj.x + obj.width < obj1.x + obj1.width \
        else False
    collision_y = True if obj1.y < obj.y < obj1.y + obj1.height or obj1.y < obj.y + obj.height < obj1.y + obj1.height\
        else False
    return collision_x and collision_y


class Colors(Enum):
    Red = (255, 0, 0)
    Blue = (0, 0, 255)
    Green = (0, 255, 0)
    Black = (0, 0, 0)
    White = (255, 255, 255)


class Directions(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    NONE = 5


class Display:
    def __init__(self, resolution):
        self.resolution = resolution
        self.object = pygame.display.set_mode(resolution)

    def fill(self, color: Colors):
        self.object.fill(color.value)

    @staticmethod
    def refresh():
        pygame.display.flip()


class GameBorders:
    def __init__(self, resolution, width, color):
        self.width = width
        self.color = color.value
        self.wall_left = pygame.Rect(0, 0, self.width, resolution[1])
        self.wall_right = pygame.Rect(resolution[0] - self.width, 0,
                                      self.width, resolution[1])
        self.wall_up = pygame.Rect(0, 0, resolution[0], self.width)
        self.wall_down = pygame.Rect(0, resolution[1] - self.width,
                                     resolution[0], self.width)
        self.walls = [self.wall_down, self.wall_right, self.wall_left, self.wall_up]

    def draw(self, g_screen: Display):
        for wall in self.walls:
            pygame.draw.rect(g_screen.object, self.color, wall)

    def check_collision(self, obj):
        for wall in self.walls:
            if is_collision(obj, wall):
                return True
        return False


class GamePart:
    def __init__(self, size, pos, color: Colors):
        self.color = color
        self.object = pygame.Rect(pos[0], pos[1], size[0], size[1])

    def draw(self, g_screen: Display):
        pygame.draw.rect(g_screen.object, self.color.value, self.object)

    def check_collision(self, obj):
        return is_collision(obj, self.object)

    def randomize_location(self, resolution, g_borders: GameBorders):
        x = randint(borders.width,
                    resolution[0] - (g_borders.width + self.object.height))
        y = randint(borders.width,
                    resolution[1] - (g_borders.width + self.object.width))
        self.object = pygame.Rect(x, y, self.object.width, self.object.height)


class SnakePart(GamePart):
    def __init__(self, speed, size, pos, direction, color):
        super().__init__(size, pos, color)
        self.speed = speed
        self.direction = direction
        self.lastMoves = deque(maxlen=int(size[0] / speed))

    def move(self):
        if self.direction == Directions.UP:
            self.object.y -= self.speed
        elif self.direction == Directions.DOWN:
            self.object.y += self.speed
        elif self.direction == Directions.LEFT:
            self.object.x -= self.speed
        elif self.direction == Directions.RIGHT:
            self.object.x += self.speed
        self.lastMoves.appendleft(self.direction)


class Snake(SnakePart):
    def __init__(self, speed, size, pos, direction: Directions, color: Colors):
        super().__init__(speed, size, pos, direction, color)
        self.body = []

    def add_body(self, body_nr):
        last_part = self if len(self.body) == 0 else self.body[-1]
        for count in range(1, body_nr + 1):
            if last_part.direction == Directions.LEFT:
                x = last_part.object.x + last_part.object.width * count
                y = last_part.object.y
            elif last_part.direction == Directions.RIGHT:
                x = last_part.object.x - last_part.object.width * count
                y = last_part.object.y
            elif last_part.direction == Directions.UP:
                x = last_part.object.x
                y = last_part.object.y + last_part.object.height * count
            else:
                x = last_part.object.x
                y = last_part.object.y - last_part.object.height * count
            newPart = SnakePart(self.speed, (self.object.width, self.object.height),
                                (x, y), self.direction, self.color)
            for i in range(int(last_part.object.width / self.speed)):
                last_part.lastMoves.append(last_part.direction)
            newPart.lastMoves = deepcopy(last_part.lastMoves)
            self.body.append(newPart)

    def determine_direction(self, e: pygame.event):
        if e.key == pygame.K_RIGHT or e.key == pygame.K_d:
            self.direction = Directions.RIGHT if self.direction != Directions.LEFT else Directions.LEFT
        elif e.key == pygame.K_LEFT or e.key == pygame.K_a:
            self.direction = Directions.LEFT if self.direction != Directions.RIGHT else Directions.RIGHT
        elif e.key == pygame.K_UP or e.key == pygame.K_w:
            self.direction = Directions.UP if self.direction != Directions.DOWN else Directions.DOWN
        elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
            self.direction = Directions.DOWN if self.direction != Directions.UP else Directions.UP

    def move_body(self):
        if len(self.body) != 0:
            direction = self.lastMoves.pop() if len(self.lastMoves) != 0 else self.direction
            for body in self.body:
                body.direction = direction
                direction = body.lastMoves.pop() if len(body.lastMoves) != 0 else body.direction
                body.move()

    def draw(self, g_screen: Display):
        pygame.draw.rect(g_screen.object, self.color.value, self.object)
        for body in self.body:
            if not borders.check_collision(body.object):
                body.draw(g_screen)
            else:
                print ("E")


SCORE = 0
DEFAULT_SPEED = 1.0
DEFAULT_BLOCK_SIZE = (20, 20)
DEFAULT_BLOCK_POSITION = (0, 0)
DEFAULT_RESOLUTION = (720, 480)
DEFAULT_BORDER_WIDTH = 15

clock = pygame.time.Clock()
# Arguments : (Screen_width, Screen height)
screen = Display(DEFAULT_RESOLUTION)
# Arguments : Screen resolution, wall width, wall, color
borders = GameBorders(screen.resolution, DEFAULT_BORDER_WIDTH, Colors.White)
# Arguments : size, pos, color
apple = GamePart(DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_POSITION, Colors.Red)
apple.randomize_location(screen.resolution, borders)
# Arguments : speed, size, pos, direction, color
snake = Snake(DEFAULT_SPEED, DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_POSITION, Directions.NONE, Colors.Green)
snake.randomize_location(screen.resolution, borders)
pause = False
# Game loop
while True:
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = False
                    break
        clock.tick(144)
    for part in snake.body[2:]:
        if snake.check_collision(part.object):
            pygame.quit()
            sys.exit()
    if borders.check_collision(snake.object):
        pygame.quit()
        sys.exit()
    if apple.check_collision(snake.object):
        SCORE += 1
        snake.add_body(3)
        correct_placement = False
        while not correct_placement:
            apple.randomize_location(screen.resolution, borders)
            for part in snake.body + [snake]:
                if apple.check_collision(part.object):
                    break
            correct_placement = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = True
            snake.determine_direction(event)
    snake.move_body()
    snake.move()

    screen.fill(Colors.Black)
    borders.draw(screen)
    apple.draw(screen)
    snake.draw(screen)
    screen.refresh()
    clock.tick(144)
