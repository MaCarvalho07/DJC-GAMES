import pygame, sys, random

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

# Inicializa Pygame e joystick
pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Controle detectado: {joystick.get_name()}")
else:
    joystick = None
    print("Nenhum controle encontrado.")

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

# Função game over
def game_over():
    font = pygame.font.SysFont('times new roman', 90)
    txt_surface = font.render('VOCÊ MORREU', True, red)
    txt_rect = txt_surface.get_rect(center=(frame_size_x / 2, frame_size_y / 4))

    btn_font = pygame.font.SysFont('times new roman', 30)
    btn_text = btn_font.render('Sair', True, white)
    btn_rect = pygame.Rect(0, 0, 120, 50)
    btn_rect.center = (frame_size_x / 2, frame_size_y / 2)

    while True:
        game_window.fill(green)
        game_window.blit(txt_surface, txt_rect)
        show_score(0, red, 'times', 20)

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
    # Input do jogador (teclado e controle)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, ord('w')]: change_to = 'UP'
            elif event.key in [pygame.K_DOWN, ord('s')]: change_to = 'DOWN'
            elif event.key in [pygame.K_LEFT, ord('a')]: change_to = 'LEFT'
            elif event.key in [pygame.K_RIGHT, ord('d')]: change_to = 'RIGHT'
            elif event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        # Entrada do controle (d-pad)
        if event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            if hat_y == 1: change_to = 'UP'
            elif hat_y == -1: change_to = 'DOWN'
            elif hat_x == -1: change_to = 'LEFT'
            elif hat_x == 1: change_to = 'RIGHT'

        # Analógico esquerdo
        if event.type == pygame.JOYAXISMOTION and joystick:
            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)
            threshold = 0.5
            if axis_y < -threshold: change_to = 'UP'
            elif axis_y > threshold: change_to = 'DOWN'
            elif axis_x < -threshold: change_to = 'LEFT'
            elif axis_x > threshold: change_to = 'RIGHT'

    # Previne reversão instantânea
    if change_to == 'UP' and direction != 'DOWN': direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP': direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT': direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT': direction = 'RIGHT'

    # Move a cabeça
    if direction == 'UP': snake_pos[1] -= block_size
    if direction == 'DOWN': snake_pos[1] += block_size
    if direction == 'LEFT': snake_pos[0] -= block_size
    if direction == 'RIGHT': snake_pos[0] += block_size

    # Adiciona nova posição ao corpo
    snake_body.insert(0, list(snake_pos))

    # Colisão com comida
    if snake_pos == food_pos:
        score += 1
        food_spawn = False
    else:
        if snake_body: snake_body.pop()

    # Spawnar comida nova
    if not food_spawn:
        food_pos = [random.randrange(0, frame_size_x // block_size) * block_size,
                    random.randrange(0, frame_size_y // block_size) * block_size]
        food_spawn = True

    # Verifica colisões
    if (
        snake_pos[0] < 0 or snake_pos[0] >= frame_size_x or
        snake_pos[1] < 0 or snake_pos[1] >= frame_size_y or
        snake_pos in snake_body[1:]
    ):
        game_over()

    # Desenhar tudo
    game_window.fill(green)
    for pos in snake_body:
        pygame.draw.rect(game_window, blue, pygame.Rect(pos[0], pos[1], 20, 20), border_radius=5)
    pygame.draw.rect(game_window, red, pygame.Rect(food_pos[0], food_pos[1], block_size, block_size), border_radius=50)

    show_score(1, white, 'consolas', 20)
    pygame.display.update()
    clock.tick(difficulty)
