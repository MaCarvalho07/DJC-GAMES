import pygame

# Inicializa o pygame e o módulo de joystick
pygame.init()
pygame.joystick.init()

# Verifica se há algum joystick conectado
if pygame.joystick.get_count() == 0:
    print("Nenhum controle conectado!")
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Controle conectado: {joystick.get_name()}")

# Janela do jogo (opcional)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Controle PS4 com Pygame")

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Detecta pressionamento de botões
        if event.type == pygame.JOYBUTTONDOWN:
            print(f"Botão pressionado: {event.button}")

        # Detecta movimento dos eixos (como os analógicos)
        if event.type == pygame.JOYAXISMOTION:
            print(f"Eixo {event.axis} movido: {event.value:.2f}")

    screen.fill((0, 0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
