import pygame, sys, random, json, os
from datetime import datetime

# Config
difficulty = 10
block_size = 30

# Inicializa Pygame
pygame.init()
pygame.display.set_caption('Snake')
game_window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
frame_size_x, frame_size_y = game_window.get_size()
clock = pygame.time.Clock()

# Cores
colors = {
    'black': pygame.Color(0, 0, 0),
    'white': pygame.Color(255, 255, 255),
    'red': pygame.Color(255, 0, 0),
    'green': pygame.Color(0, 255, 0),
    'blue': pygame.Color(0, 0, 255)
}

class Ranking:
    def __init__(self, filename='ranking_snake.json', max_entries=10):
        self.filename = filename
        self.max_entries = max_entries
        self.entries = self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.entries, f, indent=4)

    def update(self, name, score):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        found = False
        for entry in self.entries:
            if entry['name'] == name:
                if score > entry['score']:
                    entry['score'] = score
                    entry['date'] = now
                found = True
                break
        if not found:
            self.entries.append({'name': name, 'score': score, 'date': now})
        self.entries.sort(key=lambda x: x['score'], reverse=True)
        self.entries = self.entries[:self.max_entries]
        self.save()

    def get_entries(self):
        return self.entries

    def render(self, surface, pos_x, pos_y, font, color):
        for idx, entry in enumerate(self.entries):
            text = f"{idx+1}. {entry['name']} - {entry['score']} pts ({entry['date']})"
            text_surf = font.render(text, True, color)
            surface.blit(text_surf, (pos_x, pos_y + idx * 25))

class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake_pos = [block_size * 3, block_size * 3]
        self.snake_body = [list(self.snake_pos)]
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.food_pos = [random.randrange(0, frame_size_x // block_size) * block_size,
                         random.randrange(0, frame_size_y // block_size) * block_size]
        self.food_spawn = True
        self.score = 0
        self.game_over_flag = False
        self.player_name = ""
        self.input_active = False
        self.ranking = Ranking()

    def show_score(self, pos, color, font_name, size):
        font = pygame.font.SysFont(font_name, size)
        score_surf = font.render('Pontuação: ' + str(self.score), True, color)
        score_rect = score_surf.get_rect()
        if pos == 1:
            score_rect.midtop = (frame_size_x / 10, 15)
        else:
            score_rect.midtop = (frame_size_x / 2, frame_size_y / 1.25)
        game_window.blit(score_surf, score_rect)

    def game_over_screen(self):
        font_big = pygame.font.SysFont('times new roman', 90)
        txt_surface = font_big.render('VOCÊ MORREU', True, colors['red'])
        txt_rect = txt_surface.get_rect(center=(frame_size_x / 2, frame_size_y / 4))

        btn_font = pygame.font.SysFont('times new roman', 30)
        btn_text = btn_font.render('Sair', True, colors['white'])
        btn_rect = pygame.Rect(0, 0, 120, 50)
        btn_rect.center = (frame_size_x / 2, frame_size_y / 1.6)

        input_font = pygame.font.SysFont('consolas', 40)
        prompt_font = pygame.font.SysFont('times new roman', 30)
        prompt_text = prompt_font.render('Digite seu nome (Enter para confirmar):', True, colors['white'])
        prompt_rect = prompt_text.get_rect(center=(frame_size_x / 2, frame_size_y / 2 - 50))

        self.input_active = True
        self.player_name = ""

        while True:
            game_window.fill(colors['green'])
            game_window.blit(txt_surface, txt_rect)
            game_window.blit(prompt_text, prompt_rect)

            # Input box
            input_box = pygame.Rect(frame_size_x / 2 - 150, frame_size_y / 2, 300, 50)
            pygame.draw.rect(game_window, colors['white'], input_box, 2)

            name_surface = input_font.render(self.player_name, True, colors['white'])
            game_window.blit(name_surface, (input_box.x + 10, input_box.y + 5))

            self.ranking.render(game_window, 10, 10, pygame.font.SysFont('times new roman', 20), colors['white'])

            pygame.draw.rect(game_window, colors['red'], btn_rect)
            game_window.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2,
                                        btn_rect.centery - btn_text.get_height() // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.KEYDOWN and self.input_active:
                    if event.key == pygame.K_RETURN:
                        if self.player_name.strip() == "":
                            self.player_name = "Jogador"
                        self.ranking.update(self.player_name.strip(), self.score)
                        self.reset()
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, ord('w')]:
                        self.change_to = 'UP'
                    elif event.key in [pygame.K_DOWN, ord('s')]:
                        self.change_to = 'DOWN'
                    elif event.key in [pygame.K_LEFT, ord('a')]:
                        self.change_to = 'LEFT'
                    elif event.key in [pygame.K_RIGHT, ord('d')]:
                        self.change_to = 'RIGHT'
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # Previne reversão instantânea
            if self.change_to == 'UP' and self.direction != 'DOWN': self.direction = 'UP'
            if self.change_to == 'DOWN' and self.direction != 'UP': self.direction = 'DOWN'
            if self.change_to == 'LEFT' and self.direction != 'RIGHT': self.direction = 'LEFT'
            if self.change_to == 'RIGHT' and self.direction != 'LEFT': self.direction = 'RIGHT'

            # Move a cabeça
            if self.direction == 'UP': self.snake_pos[1] -= block_size
            if self.direction == 'DOWN': self.snake_pos[1] += block_size
            if self.direction == 'LEFT': self.snake_pos[0] -= block_size
            if self.direction == 'RIGHT': self.snake_pos[0] += block_size

            # Atualiza corpo da cobra
            self.snake_body.insert(0, list(self.snake_pos))

            # Come comida
            if self.snake_pos == self.food_pos:
                self.score += 1
                self.food_spawn = False
            else:
                self.snake_body.pop()

            if not self.food_spawn:
                self.food_pos = [random.randrange(0, frame_size_x // block_size) * block_size,
                                 random.randrange(0, frame_size_y // block_size) * block_size]
                self.food_spawn = True

            # Checa colisões
            if (self.snake_pos[0] < 0 or self.snake_pos[0] >= frame_size_x or
                self.snake_pos[1] < 0 or self.snake_pos[1] >= frame_size_y or
                self.snake_pos in self.snake_body[1:]):
                self.game_over_screen()

            # Desenha tudo
            game_window.fill(colors['green'])
            for pos in self.snake_body:
                pygame.draw.rect(game_window, colors['blue'], pygame.Rect(pos[0], pos[1], 20, 20), border_radius=5)
            pygame.draw.rect(game_window, colors['red'], pygame.Rect(self.food_pos[0], self.food_pos[1], block_size, block_size), border_radius=50)

            self.show_score(1, colors['white'], 'consolas', 20)
            self.ranking.render(game_window, 10, 60, pygame.font.SysFont('times new roman', 20), colors['white'])

            pygame.display.update()
            clock.tick(difficulty)


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
