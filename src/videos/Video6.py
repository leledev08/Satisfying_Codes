import pygame
import sys
import math
import random

# Inizializza Pygame
pygame.init()

# Crea la finestra
WIDGHT, HEIGHT = 1422, 800
screen_center = [WIDGHT // 2, HEIGHT // 2]
screen = pygame.display.set_mode((WIDGHT, HEIGHT))
pygame.display.set_caption("Video 6")

# Parametri del bordo
border_radius = 350
border_outline_width = 5

# Gravità
GRAVITY = 0.25

# Parametri della palla
ball_radius = 15
ball_outline_width = 5
ball_pos = screen_center.copy()
ball_color = pygame.Color(255, 255, 255)
ball_velocity = [+3, -8]
ball_acceleration = [0, GRAVITY]

# Ciclo principale
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Aggiorna la posizione della palla
    ball_velocity[0] += ball_acceleration[0]
    ball_velocity[1] += ball_acceleration[1]
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]

    # Calcola distanza dal centro
    dx = ball_pos[0] - screen_center[0]
    dy = ball_pos[1] - screen_center[1]
    distance_from_center = math.sqrt(dx**2 + dy**2)

    # Collisione con il bordo
    if distance_from_center >= border_radius - ball_radius:
        normal = [dx / distance_from_center, dy / distance_from_center]
        dot_product = (ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1])
        reflection = [ball_velocity[0] - 2 * dot_product * normal[0],
                      ball_velocity[1] - 2 * dot_product * normal[1]]
        ball_velocity = [reflection[0], reflection[1]]
        ball_pos[0] = screen_center[0] + normal[0] * (border_radius - ball_radius)
        ball_pos[1] = screen_center[1] + normal[1] * (border_radius - ball_radius)

    # Pulisci lo schermo
    screen.fill((0, 0, 0))

    # Disegna il bordo
    pygame.draw.circle(screen, (255, 255, 255), (screen_center[0], screen_center[1]), border_radius + border_outline_width)
    pygame.draw.circle(screen, (0, 0, 0), (screen_center[0], screen_center[1]), border_radius)

    # Disegna la palla
    ball_color.hsva = (0, 100, 40, 100)
    pygame.draw.circle(screen, ball_color, (ball_pos[0], ball_pos[1]), ball_radius + ball_outline_width)
    ball_color.hsva = (0, 100, 90, 100)
    pygame.draw.circle(screen, ball_color, (ball_pos[0], ball_pos[1]), ball_radius)

    # Aggiorna lo schermo
    pygame.display.flip()

    # Limita il frame rate
    pygame.time.Clock().tick(120)