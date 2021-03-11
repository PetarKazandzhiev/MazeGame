import pygame
from pygame.locals import *
import math
import random

pygame.init()

SQUARE_SIZE = 30
screen = pygame.display.set_mode((25*SQUARE_SIZE, 25*SQUARE_SIZE))

# Title and Icon
pygame.display.set_caption("The Dungeon")
icon = pygame.image.load('maze_icon.png')
pygame.display.set_icon(icon)


coin_image = pygame.image.load("coin.png")
coin_image = pygame.transform.scale(coin_image, (SQUARE_SIZE, SQUARE_SIZE))

horse_right = pygame.image.load("horse_right.png")
horse_right = pygame.transform.scale(horse_right, (SQUARE_SIZE, SQUARE_SIZE))

horse_left = pygame.image.load("horse_left.png")
horse_left = pygame.transform.scale(horse_left, (SQUARE_SIZE, SQUARE_SIZE))

enemy_image = pygame.image.load("pawn.png")
enemy_image = pygame.transform.scale(enemy_image, (SQUARE_SIZE, SQUARE_SIZE))

wall_img = pygame.image.load("wall.png")
wall_img = pygame.transform.scale(wall_img, (SQUARE_SIZE, SQUARE_SIZE))

end_screen = pygame.image.load("end_screen.png")
end_screen = pygame.transform.scale(end_screen, (25*SQUARE_SIZE, 25*SQUARE_SIZE))

win_screen = pygame.image.load("win.png")
win_screen = pygame.transform.scale(win_screen, (25*SQUARE_SIZE, 25*SQUARE_SIZE))

# when something moves , we save the previous and new coordinates in this list ,
# so  that we can redraw the characters using the function update positions
update_coordinates = []


def wall(x, y):
    screen.blit(wall_img, (x, y))


class Player:
    def __init__(self):
        self.image = horse_right
        self.gold = 0
        self.x = -1
        self.y = -1

    def goto(self, x, y):
        # Fixes the problem ,where the top wall doesn't show itself
        if self.x != -1 or self.y != -1:
            update_coordinates.append((self.x, self.y))

        update_coordinates.append((x, y))
        self.x = x
        self.y = y

    def go_down(self):
        # Calculating the spot to move to
        move_to_x = self.x
        move_to_y = self.y + SQUARE_SIZE
        # Checks if there is a wall there
        if (move_to_x, move_to_y) not in walls:
            self.goto(move_to_x, move_to_y)

    def go_up(self):
        # Calculating the spot to move to
        move_to_x = self.x
        move_to_y = self.y - SQUARE_SIZE
        # Checks if there is a wall there
        if (move_to_x, move_to_y) not in walls:
            self.goto(move_to_x, move_to_y)

    def go_left(self):
        # Calculating the spot to move to
        move_to_x = self.x - SQUARE_SIZE
        move_to_y = self.y
        self.image = horse_left
        # Checks if there is a wall there
        if (move_to_x, move_to_y) not in walls:
            self.goto(move_to_x, move_to_y)

    def go_right(self):
        # Calculating the spot to move to
        move_to_x = self.x + SQUARE_SIZE
        move_to_y = self.y
        self.image = horse_right
        # Checking if this space is a wall
        if (move_to_x, move_to_y) not in walls:
            self.goto(move_to_x, move_to_y)

    def is_collision(self, other):
        # Returns True or false based on weather or not there is a collision
        return self.x == other.x and self.y == other.y


class Treasure:
    def __init__(self, x, y):
        self.gold = 100
        self.x = x
        self.y = y
        self.image = coin_image
        screen.blit(coin_image, (x, y))


class Enemy:
    def __init__(self, x, y):
        self.image = enemy_image
        self.y = y
        self.x = x
        self.speed = 2
        self.max_delay = 500
        self.max_tries = 100
        self.tries = 0
        self.delay = self.max_delay
        self.direction = random.choice(["up", "down", "left", "right"])
        self.last_direction = self.direction
        screen.blit(enemy_image, (x, y))

    def move(self):
        if self.delay <= 0:
            self.go_direction(self.direction)
            self.delay = self.max_delay
        else:
            self.delay -= self.speed

    def go_direction(self, go_dir):
        # checks if we must chase the player
        if self.is_close(player):
            if self.y > player.y:
                go_dir = "up"
            elif self.y < player.y:
                go_dir = "down"
            elif self.x < player.x:
                go_dir = "right"
            elif self.x > player.x:
                go_dir = "left"

        elif self.last_direction != "":
            # Tried to make the enemy smarter by  adding 3 times the last direction to the list
            # so that it is more likely for the enemy to choose
            # the same direction(because the maze has a lot of long corridors
            possible_directions = ["down", "up", "left", "right"]
            possible_directions.append(self.last_direction)
            possible_directions.append(self.last_direction)
            possible_directions.append(self.last_direction)
            go_dir = random.choice(possible_directions)
        # Calculating the spot to move to
        if go_dir == "up":
            move_to_x = self.x
            move_to_y = self.y - SQUARE_SIZE
        elif go_dir == "down":
            move_to_x = self.x
            move_to_y = self.y + SQUARE_SIZE
        elif go_dir == "left":
            move_to_x = self.x - SQUARE_SIZE
            move_to_y = self.y
        elif go_dir == "right":
            move_to_x = self.x + SQUARE_SIZE
            move_to_y = self.y

        if (move_to_x, move_to_y) not in walls:
            self.tries = 0
            self.goto(move_to_x, move_to_y)
            self.last_direction = go_dir

        elif self.tries < self.max_tries:
            possible_directions = ["down", "up", "left", "right"]
            possible_directions.remove(go_dir)
            self.last_direction = ""
            self.direction = random.choice(possible_directions)
            self.delay = 0
            self.tries += 1
            self.move()
        else:
            self.last_direction = ""

    # Makes the Player move
    def goto(self, x, y):
        # previous coordinates
        update_coordinates.append((self.x, self.y))
        # next coordinates
        update_coordinates.append((x, y))
        self.x = x
        self.y = y

    # Tried to make the enemy smarter by chasing the player whenever he is near
    def is_close(self, other):
        a = self.x-other.x
        b = self.y-other.y
        # this is a function that measures the distance between the coordinates of
        # the player and the enemy
        distance = math.sqrt((a ** 2) + (b ** 2))
        # if the distance is less than 3 squares the enemy chases the player
        if distance < 3*SQUARE_SIZE:
            return True
        else:
            return False


# Creating list of walls
walls = []

# Creating list of enemies
enemies = []

# Creating list of treasures
treasures = []

# Create list of levels
levels = [" "]

# Create first level
level_1 = [
    "XXXXXXXXXXXXXXXXXXXXXXXXX",
    "XT     P      X         X",
    "X XXXXXXXXXXX X XXXXXX XX",
    "X XXXXX    XX X  XTTTXT X",
    "X    T  XX XX XETXTTTX  X",
    "X XXXXXXXX XX XXXXTTTX XX",
    "X X    X   XX XXXXX X T X",
    "X X X XX XXXX  T  X X X X",
    "X X X  T    XXXXX X X X X",
    "X   XX T XXXX   E X T X X",
    "XXXXX         XXXXXXXXX X",
    "XXXXXXXXX XXX X  T      X",
    "XTEX      XXX X XXXXXXXXX",
    "X XX XXXXXXXX X X   X   X",
    "X XX  XXXX    X X X   XXX",
    "X XXX    X XXXX E XXX   X",
    "X   XXXX X XXXXXXXXXX XXX",
    "XT  X    X      X   X T X",
    "X   X XXXXXXXXX X X XXX X",
    "XXX X XX        X X X T X",
    "X      T XXXXXXXX X XTXXX",
    "X XXXXXX      T   X X T X",
    "X  T   XXXXXXXXXXXX XXX X",
    "X XXXX   E  T    T      X",
    "XXXXXXXXXXXXXXXXXXXXXXXXX"
]
levels.append(level_1)

player = Player()


def setup_maze(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            # Character at each x,y coordinate
            character = level_1[y][x]
            # Calculate the screen x, y coordinates
            screen_x = (x * SQUARE_SIZE)
            screen_y = (y * SQUARE_SIZE)

            # Checking if it is an X(X is representing the wall)
            if character == "X":
                wall(screen_x, screen_y)
                walls.append((screen_x, screen_y))

            # Checking if it is an P(P is representing the player)
            if character == "P":
                player.goto(screen_x, screen_y)

                # Checking if it is a T(representing the treasure)
            if character == "T":
                treasures.append(Treasure(screen_x, screen_y))

            # Checking if it is a E(representing the enemy)
            if character == "E":
                enemies.append(Enemy(screen_x, screen_y))


def update_positions():
    for i in range(len(update_coordinates)):
        # draws on the screen a rectangle with the set size and coordinates
        pygame.draw.rect(screen, (128, 128, 128), (update_coordinates[i][0], update_coordinates[i][1], SQUARE_SIZE, SQUARE_SIZE))
        # draws the player
        if player.x == update_coordinates[i][0] and player.y == update_coordinates[i][1]:
            screen.blit(player.image, (player.x, player.y))
        else:
            for j in range(len(treasures)):
                if treasures[j].x == update_coordinates[i][0] and treasures[j].y == update_coordinates[i][1]:
                    screen.blit(treasures[j].image, (treasures[j].x, treasures[j].y))
                    break
            for j in range(len(enemies)):
                if enemies[j].x == update_coordinates[i][0] and enemies[j].y == update_coordinates[i][1]:
                    screen.blit(enemies[j].image, (enemies[j].x, enemies[j].y))
                    break
        # So that we don't update the coordinates again
    update_coordinates.clear()


screen.fill((128, 128, 128))
setup_maze(levels[1])

# Game Loop
running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == pygame.K_LEFT:
                player.go_left()
            elif event.key == pygame.K_RIGHT:
                player.go_right()
            elif event.key == pygame.K_UP:
                player.go_up()
            elif event.key == pygame.K_DOWN:
                player.go_down()

    for enemy in enemies:
        if player.is_collision(enemy):
            screen.blit(end_screen, (0, 0))
            game_over = True

        enemy.direction = random.choice(["up", "down", "left", "right"])
        enemy.move()

    for treasure in treasures:
        if player.is_collision(treasure) and not game_over:
            player.gold += treasure.gold
            pygame.display.set_caption("The Dungeon- Score: {}".format(player.gold))
            treasures.remove(treasure)
            if player.gold >= 3000:
                screen.blit(win_screen, (0, 0))
                game_over = True
    if not game_over:
        update_positions()

    pygame.display.update()
