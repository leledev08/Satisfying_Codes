import pygame
import math
import random

pygame.init()

# Risoluzione verticale per short
WIDTH, HEIGHT = 1080, 1920
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Palline che si duplicano dal centro")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

scale = HEIGHT / 1280
center_x, center_y = WIDTH // 2, HEIGHT // 2
margin = 50
circle_radius = min(center_x, center_y) - margin

# Velocità base e range
base_speed = 3.5 * scale * 0.60
min_speed = base_speed * 0.8
max_speed = base_speed * 1.4

# Raggio iniziale
initial_radius = int(80 * scale)

# Tavolozza colori accesi
bright_colors = [
    (255, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (0, 255, 0),
    (148, 0, 211),
    (255, 20, 147),
    (255, 140, 0),
    (0, 255, 255),
]

def random_bright_color():
    return random.choice(bright_colors)

# Lista palline: [x, y, dx, dy, radius, color]
balls = [[center_x, center_y, base_speed, -base_speed, initial_radius, random_bright_color()]]

# Suono rimbalzo
bounce_sound = pygame.mixer.Sound("assets/sounds/pop.mp3")

clock = pygame.time.Clock()
running = True
paused = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = False

    if not paused:
        new_balls = []
        for ball in balls:
            x, y, dx, dy, radius, color = ball
            x += dx
            y += dy

            dist = math.hypot(x - center_x, y - center_y)
            if dist + radius >= circle_radius:
                bounce_sound.play()

                # Riduzione dimensione
                new_radius = radius * 0.7

                # Due nuove palline dal centro
                for _ in range(2):
                    angle_new = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(min_speed, max_speed)
                    new_balls.append([
                        center_x,
                        center_y,
                        speed * math.cos(angle_new),
                        speed * math.sin(angle_new),
                        new_radius,
                        random_bright_color()
                    ])
            else:
                new_balls.append([x, y, dx, dy, radius, color])

        balls = new_balls

    # Sfondo
    screen.fill(BLACK)

    # Cerchio pieno nero
    pygame.draw.circle(screen, BLACK, (center_x, center_y), circle_radius)

    # Bordo giallo
    pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), circle_radius, 4)

    # Disegno palline
    for x, y, _, _, radius, color in balls:
        pygame.draw.circle(screen, color, (int(x), int(y)), max(1, int(radius)))

    pygame.display.flip()

pygame.quit()
