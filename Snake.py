import pygame
import sys
import random
from math import fabs


class Colors:
    Black = [0, 0, 0]
    White = [255, 255, 255]
    Red = [255, 0, 0]
    Green = [0, 255, 0]
    Blue = [0, 0, 255]

    @staticmethod
    def custom_color(r, g, b):
        return [r, g, b]


class Menu:
    def __init__(self, height, width, color, font, score_coord, game_over_coord):
        self.height = height
        self.width = width
        self.color = color
        self.font = font
        self.score_coord = score_coord
        self.game_over_coord = game_over_coord
        self.object = pygame.Rect(0, 0, width, height)

    def update(self, screen_var, score_var, game_over=False):
        pygame.draw.rect(screen_var, self.color, self.object)
        score_text = self.font.render('Score: ' + str(score_var), False, Colors.Red)
        if game_over:
            game_over_text = self.font.render("Game over ! Press space to restart", False, Colors.Red)
            Screen.Screen.blit(game_over_text, self.game_over_coord)
        Screen.Screen.blit(score_text, self.score_coord)


class Display:
    Default_resolution = (1280, 720)
    Resolution = None
    Screen = None

    def __init__(self, resolution=Default_resolution):
        self.Resolution = resolution
        self.Screen = pygame.display.set_mode(resolution)

    def fill(self, color):
        self.Screen.fill(color)

    @staticmethod
    def refresh():
        pygame.display.flip()


class GameBorders:
    Width = 0
    Color = None
    Wall_left = None
    Wall_right = None
    Wall_up = None
    Wall_down = None
    Borders = []

    def __init__(self, menu_height, screen: Display, width=10, color=None):
        if color is None:
            color = Colors.White
        self.Width = width
        self.Color = color
        screen_resolution = screen.Resolution
        self.Wall_left = pygame.Rect(0, 0, self.Width, screen_resolution[1])
        self.Wall_right = pygame.Rect(screen_resolution[0] - self.Width, 0,
                                      self.Width, screen_resolution[1])
        self.Wall_up = pygame.Rect(0, menu_height, screen_resolution[0], self.Width)
        self.Wall_down = pygame.Rect(0, screen_resolution[1] - self.Width,
                                     screen_resolution[0], self.Width)
        self.Borders = [self.Wall_down, self.Wall_right, self.Wall_left, self.Wall_up]

    def draw(self, screen: Display):
        pygame.draw.rect(screen.Screen, self.Color, self.Wall_left)
        pygame.draw.rect(screen.Screen, self.Color, self.Wall_right)
        pygame.draw.rect(screen.Screen, self.Color, self.Wall_up)
        pygame.draw.rect(screen.Screen, self.Color, self.Wall_down)

    def check_collision(self, player):
        for border in self.Borders:
            x_collision, y_collision = check_collision(player.Head, border)
            if x_collision and y_collision:
                return True
        return False


class SnakeBody:
    # Snake body attributes
    # Color = []
    Self = None
    X = 0
    Y = 0
    # Snake move attributes
    Movement = ""
    Speed = 0
    Move_pos = ()
    Height = None
    Width = None

    def __init__(self, x, y, height, width, speed, color):
        self.Width = width
        self.Height = height
        self.Speed = speed
        self.Color = color
        self.X = x
        self.Y = y
        self.Self = pygame.Rect(int(self.X), int(self.Y), self.Width, self.Height)

    def update_location(self):
        self.Self = pygame.Rect(int(self.X), int(self.Y), self.Width, self.Height)

    def move_to_object(self, obj: pygame.Rect):
        if self.Move_pos == ():
            self.Move_pos = obj.x, obj.y
        if self.X == self.Move_pos[0] and self.Y == self.Move_pos[1]:
            self.Move_pos = obj.x, obj.y
        move_x, move_y = self.Move_pos
        if self.X != move_x:
            if self.X < move_x:
                if fabs(self.X - move_x) < self.Speed:
                    self.X = move_x + (self.Speed - fabs(self.Y - move_y))
                    self.Move_pos = ()
                else:
                    self.X += self.Speed
                self.Movement = "RIGHT"
            else:
                if fabs(self.X - move_x) < self.Speed:
                    self.X = move_x - (self.Speed - fabs(self.Y - move_y))
                else:
                    self.X -= self.Speed
                self.Movement = "LEFT"
        else:
            if self.Y < move_y:
                if fabs(self.Y - move_y) < self.Speed:
                    self.Y = move_y + (self.Speed - fabs(self.Y - move_y))
                    self.Move_pos = ()
                else:
                    self.Y += self.Speed
                self.Movement = "DOWN"
            else:
                if fabs(self.Y - move_y) <= self.Speed:
                    self.Y = move_y - (self.Speed - fabs(self.Y - move_y))
                    self.Move_pos = ()
                else:
                    self.Y -= self.Speed
                self.Movement = "UP"

        self.update_location()


class Snake:
    # Snake attributes
    Color = []
    # Snake move attributes
    Speed = 0
    Movement = ""
    Last_move_pos = ()
    # Snake head attributes
    Head = None
    Head_x = 0
    Head_y = 0
    Head_height = None
    Head_width = None

    # Snake body attributes
    Body = []
    Body_height = None
    Body_width = None

    def __init__(self, x_pos=20, y_pos=20, height=50, width=50, speed=2.0, color=None):
        if color is None:
            color = Colors.White
        self.Color = color
        self.Speed = speed
        self.Head_x = x_pos
        self.Head_y = y_pos
        self.Head_width = self.Body_width = width
        self.Head_height = self.Body_height = height

        self.Head = pygame.Rect(self.Head_x, self.Head_y, self.Head_width, self.Head_height)

    def randomize_location(self, screen: Display, borders: GameBorders, var_menu: Menu):
        self.Head_x = random.randint(borders.Width,
                                     screen.Resolution[0] - (borders.Width + self.Head_width))
        self.Head_y = random.randint(Borders.Width + var_menu.height,
                                     screen.Resolution[1] - (borders.Width + self.Head_height))
        self.update_head_location()

    def determine_movement(self, events):
        if (events.key == pygame.K_w or events.key == pygame.K_UP) and not self.Movement == "DOWN":
            self.Movement = "UP"
        if (events.key == pygame.K_s or events.key == pygame.K_DOWN) and not self.Movement == "UP":
            self.Movement = "DOWN"
        if (events.key == pygame.K_a or events.key == pygame.K_LEFT) and not self.Movement == "RIGHT":
            self.Movement = "LEFT"
        if (events.key == pygame.K_d or events.key == pygame.K_RIGHT) and not self.Movement == "LEFT":
            self.Movement = "RIGHT"

    def cancel_movement(self, events):

        if events.key == pygame.K_SPACE or events.key == pygame.K_w or events.key == pygame.K_UP:
            self.Movement = "DOWN"
        if events.key == pygame.K_s or events.key == pygame.K_DOWN:
            self.Movement = "UP"
        if events.key == pygame.K_a or events.key == pygame.K_LEFT:
            self.Movement = "RIGHT"
        if events.key == pygame.K_d or events.key == pygame.K_RIGHT:
            self.Movement = "LEFT"

    def update_head_location(self):
        self.Head = pygame.Rect(int(self.Head_x), int(self.Head_y), self.Head_width,
                                self.Head_height)

    def check_collision(self, obj):
        collide_x, collide_y = check_collision(self.Head, obj)
        return collide_x, collide_y

    def check_body_collision(self):
        for part in snake.Body[1:]:
            part: SnakeBody
            x_collide, y_collide = self.check_collision(part.Self)
            if x_collide and y_collide:
                return True
        return False

    def add_body(self, body_nr):
        movement = self.Movement
        x = self.Head_x
        y = self.Head_y
        width = self.Head_width
        height = self.Head_height
        if len(self.Body) != 0:
            last = self.Body[len(self.Body)-1]
            last: SnakeBody
            movement = last.Movement
            x = last.X
            y = last.Y
            width = last.Width
            height = last.Height
        for i in range(body_nr):
            if movement == "UP":
                snake_body = SnakeBody(x,
                                       y + height,
                                       self.Body_width,
                                       self.Body_height,
                                       self.Speed,
                                       self.Color,
                                       )
            elif movement == "DOWN":
                snake_body = SnakeBody(x,
                                       y - height,
                                       self.Body_width,
                                       self.Body_height,
                                       self.Speed,
                                       self.Color
                                       )
            elif movement == "LEFT":
                snake_body = SnakeBody(x + width,
                                       y,
                                       self.Body_width,
                                       self.Body_height,
                                       self.Speed,
                                       self.Color
                                       )
            else:
                snake_body = SnakeBody(x - width,
                                       y,
                                       self.Body_width,
                                       self.Body_height,
                                       self.Speed,
                                       self.Color
                                       )
            snake_body.Movement = movement
            self.Body.append(snake_body)
            last = self.Body[len(self.Body)-1]
            movement = last.Movement
            x = last.X
            y = last.Y
            width = last.Width
            height = last.Height

    def move_body(self):
        next_part = self.Head  # check where it is after next loop
        for part in self.Body:
            part: SnakeBody
            current_part = part.Self
            part.move_to_object(next_part)
            next_part = current_part

    def move_head(self):
        if self.Movement == "UP":
            self.Head_y -= self.Speed
        if self.Movement == "DOWN":
            self.Head_y += self.Speed
        if self.Movement == "LEFT":
            self.Head_x -= self.Speed
        if self.Movement == "RIGHT":
            self.Head_x += self.Speed
        self.update_head_location()

    def draw(self, screen: Display):
        if len(self.Body) != 0:
            for body_part in self.Body:
                body_part: SnakeBody
                pygame.draw.rect(screen.Screen, self.Color, body_part.Self)
        pygame.draw.rect(screen.Screen, self.Color, snake.Head)


class Apple:
    color = None
    x = 0
    y = 0
    Height = 0
    Width = 0
    Self = None

    def __init__(self, color=None, x_pos=30, y_pos=30, height=20, width=20):
        if color is None:
            color = Colors.Red
        self.x = x_pos
        self.y = y_pos
        self.color = color
        self.Height = height
        self.Width = width
        self.Self = pygame.Rect(self.x, self.y, self.Width, self.Height)

    def update_location(self):
        self.Self = pygame.Rect(self.x, self.y, self.Width, self.Height)

    def draw(self, screen: Display):
        pygame.draw.rect(screen.Screen, self.color, self.Self)

    def randomize_location(self, screen: Display, borders: GameBorders, var_menu: Menu):
        self.x = random.randint(borders.Width,
                                screen.Resolution[0] - (borders.Width + self.Height))
        self.y = random.randint(Borders.Width + var_menu.height,
                                screen.Resolution[1] - (borders.Width + self.Width))
        self.update_location()

    def check_collision(self, obj):
        collide_x, collide_y = check_collision(obj, self.Self)
        return collide_x and collide_y


def check_collision(obj: pygame.Rect, obj1: pygame.Rect):
    collision_in_x = False
    collision_in_y = False
    if obj1.x != 0:
        if obj.x + obj.width > obj1.x and obj.x < obj1.x + obj1.width:
            collision_in_x = True
    else:
        if obj.x < obj1.x + obj1.width:
            collision_in_x = True
    if obj1.y != 0:
        if obj.y + obj.height > obj1.y and obj.y < obj1.y + obj1.height:
            collision_in_y = True
    else:
        if obj.y < obj1.y + obj1.height:
            collision_in_y = True
    return collision_in_x, collision_in_y


pygame.font.init()
menu_font = pygame.font.SysFont('Comic Sans MS', 15)
menu_size = 40
menu_color = Colors.White
score_coordinates = (15, 5)
game_over_coordinates = (90, 5)
menu = Menu(menu_size, 720, menu_color, menu_font, score_coordinates, game_over_coordinates)

Clock = pygame.time.Clock()
# Arguments : (Screen_width, Screen height)
Screen = Display((720, 480))
# Arguments : Screen resolution, wall width, wall, color
Borders = GameBorders(menu.height, Screen, 15, Colors.White)
# Arguments : color, x, y, height, width
Apple = Apple(Colors.Red, 0, 0, 20, 20)
Apple.randomize_location(Screen, Borders, menu)
# Arguments : x, y, height, width, speed, color
snake = Snake(0, 0, 20, 20, 1.0, Colors.Green)
snake.randomize_location(Screen, Borders, menu)
# Game loop
Score = 0
Restart = False
while True:
    while True:
        snake.Changed_directions = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == pygame.KEYUP:
            # cancel_movement(event)
            if event.type == pygame.KEYDOWN:
                snake.determine_movement(event)
        if Borders.check_collision(snake):
            break
        if snake.check_body_collision():
            break
        if Apple.check_collision(snake.Head):
            Apple.randomize_location(Screen, Borders, menu)
            snake.add_body(3)
            Score += 1
            print(Score)
        snake.move_head()
        snake.move_body()
        Screen.fill(Colors.Black)
        Borders.draw(Screen)
        menu.update(Screen.Screen, Score)
        Apple.draw(Screen)
        snake.draw(Screen)
        Screen.refresh()
        Clock.tick(144)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    Restart = True
        if Restart:
            Screen.fill(Colors.Black)
            Screen.refresh()
            Apple.randomize_location(Screen, Borders, menu)
            snake.Body = []
            snake.Movement = ""
            snake.randomize_location(Screen, Borders, menu)
            Restart = False
            Score = 0
            break
        Screen.fill(Colors.Red)
        menu.update(Screen.Screen, Score, True)
        Screen.refresh()
        Clock.tick(144)
