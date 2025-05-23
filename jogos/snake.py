import pygame, sys, random, json, os

# Config
difficulty = 10
frame_size_x = 720
frame_size_y = 480

# Cores
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

# Inicializa Pygame
pygame.init()
pygame.display.set_caption('Snake')
game_window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
frame_size_x, frame_size_y = game_window.get_size()

# FPS
clock = pygame.time.Clock()

# Variáveis do jogo
block_size = 30
snake_pos = [block_size * 3, block_size * 3]
snake_body = [list(snake_pos)]
direction = 'RIGHT'
change_to = direction

food_pos = [random.randrange(0, frame_size_x // block_size) * block_size,
            random.randrange(0, frame_size_y // block_size) * block_size]
food_spawn = True

score = 0

# Arquivo de ranking
ranking_file = 'ranking_snake.json'

# Função para carregar ranking
def load_ranking():
    if os.path.exists(ranking_file):
        with open(ranking_file, 'r') as f:
            return json.load(f)
    else:
        return []

# Função para salvar ranking
def save_ranking(name, score):
    ranking = load_ranking()
    ranking.append({'name': name, 'score': score})
    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)[:5]
    with open(ranking_file, 'w') as f:
        json.dump(ranking, f, indent=4)

# Função para mostrar ranking
def show_ranking():
    ranking = load_ranking()
    font = pygame.font.SysFont('times new roman', 20)
    for idx, entry in enumerate(ranking):
        text = f"{idx + 1}. {entry['name']} - {entry['score']}"
        text_surface = font.render(text, True, white)
        game_window.blit(text_surface, (10, 10 + idx * 25))

# Função game over
def game_over():
    font = pygame.font.SysFont('times new roman', 90)
    txt_surface = font.render('VOCÊ MORREU', True, red)
    txt_rect = txt_surface.get_rect(center=(frame_size_x / 2, frame_size_y / 4))

    btn_font = pygame.font.SysFont('times new roman', 30)
    btn_text = btn_font.render('Sair', True, white)
    btn_rect = pygame.Rect(0, 0, 120, 50)
    btn_rect.center = (frame_size_x / 2, frame_size_y / 2)

    # Pega o nome do jogador
    name = input("Digite seu nome: ").strip() or "Jogador"

    # Salva no ranking
    save_ranking(name, score)

    while True:
        game_window.fill(green)
        game_window.blit(txt_surface, txt_rect)
        show_score(0, red, 'times', 20)
        show_ranking()

        pygame.draw.rect(game_window, red, btn_rect)
        game_window.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2,
                                    btn_rect.centery - btn_text.get_height() // 2))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.MOUSEBUTTONDOWN and btn_rect.collidepoint(event.pos)
            ):
                pygame.quit()
                sys.exit()

# Mostrar score
def show_score(pos, color, font, size):
    score_font = pygame.font.SysFont(font, 50)
    score_surf = score_font.render('Pontuação: ' + str(score), True, color)
    score_rect = score_surf.get_rect()
    if pos == 1:
        score_rect.midtop = (frame_size_x / 10, 15)
    else:
        score_rect.midtop = (frame_size_x / 2, frame_size_y / 1.25)
    game_window.blit(score_surf, score_rect)

# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, ord('w')]: change_to = 'UP'
            elif event.key in [pygame.K_DOWN, ord('s')]: change_to = 'DOWN'
            elif event.key in [pygame.K_LEFT, ord('a')]: change_to = 'LEFT'
            elif event.key in [pygame.K_RIGHT, ord('d')]: change_to = 'RIGHT'
            elif event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

    if change_to == 'UP' and direction != 'DOWN': direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP': direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT': direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT': direction = 'RIGHT'

    if direction == 'UP': snake_pos[1] -= block_size
    if direction == 'DOWN': snake_pos[1] += block_size
    if direction == 'LEFT': snake_pos[0] -= block_size
    if direction == 'RIGHT': snake_pos[0] += block_size

    snake_body.insert(0, list(snake_pos))

    if snake_pos == food_pos:
        score += 1
        food_spawn = False
    else:
        if snake_body: snake_body.pop()

    if not food_spawn:
        food_pos = [random.randrange(0, frame_size_x // block_size) * block_size,
                    random.randrange(0, frame_size_y // block_size) * block_size]
        food_spawn = True

    if (
        snake_pos[0] < 0 or snake_pos[0] >= frame_size_x or
        snake_pos[1] < 0 or snake_pos[1] >= frame_size_y or
        snake_pos in snake_body[1:]
    ):
        game_over()

    game_window.fill(green)
    for pos in snake_body:
        pygame.draw.rect(game_window, blue, pygame.Rect(pos[0], pos[1], 20, 20), border_radius=5)
    pygame.draw.rect(game_window, red, pygame.Rect(food_pos[0], food_pos[1], block_size, block_size), border_radius=50)

    show_score(1, white, 'consolas', 20)
    show_ranking()

    pygame.display.update()
    clock.tick(difficulty)
