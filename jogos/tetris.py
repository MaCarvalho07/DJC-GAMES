import pygame
import random
import time
import os

colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]


class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation - 1) % len(self.figures[self.type])


class Tetris:
    def __init__(self, height, width, screen_width, screen_height):
        self.level = 2
        self.score = 0
        self.state = "start"
        self.field = []
        self.height = height
        self.width = width
        
        # Calculate zoom factor based on screen size
        self.zoom = min(screen_width // (width + 10), screen_height // (height + 3))
        
        # Center the game field on screen
        self.x = (screen_width - self.zoom * width) // 2
        self.y = (screen_height - self.zoom * height) // 2
        
        self.figure = None
    
        # Initialize the field
        self.field = []
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        self.figure = Figure(3, 0)

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation


# Initialize the game engine
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Get the screen info
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

# Set the screen to fullscreen
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

pygame.display.set_caption("Tetris Fullscreen")

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10, screen_width, screen_height)
counter = 0

pressing_down = False

while not done:
    if game.figure is None:
        game.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0

    if counter % (fps // game.level // 2) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
                pressing_down = False
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
                pressing_down = False
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
                pressing_down = False
            if event.key == pygame.K_SPACE:
                game.go_space()
                pressing_down = False
            if event.key == pygame.K_ESCAPE:
                # Reset game or exit
                if game.state == "gameover":
                    game = Tetris(20, 10, screen_width, screen_height)
                else:
                    done = True
            if event.key == pygame.K_f:
                # Toggle fullscreen
                pygame.display.toggle_fullscreen()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

    screen.fill(BLACK)

    # Draw game field
    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

    # Draw current figure
    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])

    # Calculate font sizes based on screen dimensions
    font_size = max(int(screen_height / 25), 20)
    big_font_size = max(int(screen_height / 40), 14)
    
    font = pygame.font.SysFont('Calibri', font_size, True, False)
    font1 = pygame.font.SysFont('Calibri', big_font_size, True, False)
    
    # Draw score
    text = font.render("Score: " + str(game.score), True, WHITE)
    screen.blit(text, [game.x, game.y - font_size - 10])
    
    # Draw controls info
    controls_text = font.render("Controls: Arrows, Space, ESC to exit, F to toggle fullscreen", True, WHITE)

    # Calcular a posição centralizada
    center_x = (screen_width - controls_text.get_width()) // 2

    # Aplicar um deslocamento menor para a esquerda
    offset = -5 
    controls_x = center_x + offset

    # Garantir que o texto não saia da tela pela esquerda
    controls_x = max(20, controls_x) 

    # Desenhar o texto na posição calculada
    screen.blit(controls_text, [controls_x, screen_height - font_size - 5])
    
    # Game over text
    if game.state == "gameover":
        text_game_over = font1.render("Game Over", True, (255, 125, 0))
        text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))
        
        # Center the game over text
        go_width = text_game_over.get_width()
        go_height = text_game_over.get_height()
        screen.blit(text_game_over, [(screen_width - go_width) // 2, (screen_height - go_height) // 2 - go_height])
        
        # Center the press ESC text
        esc_width = text_game_over1.get_width()
        esc_height = text_game_over1.get_height()
        screen.blit(text_game_over1, [(screen_width - esc_width) // 2, (screen_height - esc_height) // 2 + 10])

    pygame.display.flip()
    clock.tick(fps)




pygame.quit()