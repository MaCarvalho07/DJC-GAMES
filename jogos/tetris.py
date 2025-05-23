import pygame
import random
import os
import json

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
        self.zoom = min(screen_width // (width + 10), screen_height // (height + 3))
        self.x = (screen_width - self.zoom * width) // 2
        self.y = (screen_height - self.zoom * height) // 2
        self.figure = None
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        self.figure = Figure(3, 0)

    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        return True
        return False

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

# Funções de ranking
RANK_FILE = "ranking.json"

def load_ranking():
    if os.path.exists(RANK_FILE):
        with open(RANK_FILE, "r") as f:
            return json.load(f)
    return []

def save_ranking(ranking):
    with open(RANK_FILE, "w") as f:
        json.dump(ranking, f)

def add_score(name, score):
    ranking = load_ranking()
    ranking.append({"name": name, "score": score})
    ranking.sort(key=lambda x: x["score"], reverse=True)
    save_ranking(ranking[:10])  # mantém só top 10

# Pygame
pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Tetris Rank")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

font = pygame.font.SysFont('Calibri', 40, True, False)
small_font = pygame.font.SysFont('Calibri', 30, True, False)

clock = pygame.time.Clock()
fps = 25

def draw_text_center(text, y):
    txt = font.render(text, True, WHITE)
    screen.blit(txt, ((screen_width - txt.get_width()) // 2, y))

def menu():
    while True:
        screen.fill(BLACK)
        draw_text_center("1 - Jogar", screen_height//3)
        draw_text_center("2 - Ver Ranking", screen_height//3 + 50)
        draw_text_center("ESC - Sair", screen_height//3 + 100)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "jogar"
                if event.key == pygame.K_2:
                    return "ranking"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); exit()

def get_player_name():
    name = ""
    while True:
        screen.fill(BLACK)
        draw_text_center("Digite seu nome: " + name, screen_height // 2)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name != "":
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10 and event.unicode.isalnum():
                    name += event.unicode

def show_ranking():
    ranking = load_ranking()
    screen.fill(BLACK)
    draw_text_center("Ranking", 50)
    for idx, entry in enumerate(ranking):
        txt = f"{idx+1}. {entry['name']} - {entry['score']}"
        text = small_font.render(txt, True, WHITE)
        screen.blit(text, (100, 150 + idx * 40))
    draw_text_center("Pressione qualquer tecla para voltar", screen_height - 50)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False
            if event.type == pygame.QUIT:
                pygame.quit(); exit()

while True:
    choice = menu()
    if choice == "ranking":
        show_ranking()
    elif choice == "jogar":
        player_name = get_player_name()
        game = Tetris(20, 10, screen_width, screen_height)
        counter = 0
        pressing_down = False
        done = False
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
                    pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game.rotate()
                    if event.key == pygame.K_DOWN:
                        pressing_down = True
                    if event.key == pygame.K_LEFT:
                        game.go_side(-1)
                    if event.key == pygame.K_RIGHT:
                        game.go_side(1)
                    if event.key == pygame.K_SPACE:
                        game.go_space()
                    if event.key == pygame.K_ESCAPE:
                        done = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        pressing_down = False

            screen.fill(BLACK)
            for i in range(game.height):
                for j in range(game.width):
                    pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
                    if game.field[i][j] > 0:
                        pygame.draw.rect(screen, colors[game.field[i][j]], [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

            if game.figure is not None:
                for i in range(4):
                    for j in range(4):
                        p = i * 4 + j
                        if p in game.figure.image():
                            pygame.draw.rect(screen, colors[game.figure.color], [game.x + game.zoom * (j + game.figure.x) + 1, game.y + game.zoom * (i + game.figure.y) + 1, game.zoom - 2, game.zoom - 2])

            score_text = small_font.render("Score: " + str(game.score), True, WHITE)
            screen.blit(score_text, [game.x, game.y - 30])

            if game.state == "gameover":
                draw_text_center("Game Over", screen_height // 2)
                draw_text_center("Pressione ESC", screen_height // 2 + 50)
                add_score(player_name, game.score)

            pygame.display.flip()
            clock.tick(fps)
