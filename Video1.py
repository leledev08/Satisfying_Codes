import pygame
import math
import colorsys

pygame.init()

BASE_WIDTH, BASE_HEIGHT = 720, 1280
WIDTH, HEIGHT = 1080, 1920
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pallina che si ingrandisce e rimbalza")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

scale_x = WIDTH / BASE_WIDTH
scale_y = HEIGHT / BASE_HEIGHT
scale = (scale_x + scale_y) / 2  # scala media per mantenere proporzioni

center_x, center_y = WIDTH // 2, HEIGHT // 2
circle_radius = int(320 * scale)

# Pallina
ball_x, ball_y = center_x, center_y - int(60 * scale)
ball_radius = int(15 * scale)
ball_dx, ball_dy = 6 * scale, -4 * scale
gravity = 0.5 * scale

# Restituzione
restitution = 1.022

# Colori dinamici
hue = 0
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Glow attorno al bordo
circle_glow_time = None
circle_glow_duration = 0.4  # secondi

# Suono rimbalzo
bounce_sound = pygame.mixer.Sound("assets/sounds/pingpong.mp3")

clock = pygame.time.Clock()
running = True
paused = True

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

old_ball_x, old_ball_y = ball_x, ball_y

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = False

    if not paused:
        old_ball_x, old_ball_y = ball_x, ball_y

        # Aggiorna posizione con gravità
        ball_dy += gravity
        ball_x += ball_dx
        ball_y += ball_dy

        dist = math.hypot(ball_x - center_x, ball_y - center_y)
        bounced = False

        if dist + ball_radius >= circle_radius:
            nx = (ball_x - center_x) / dist
            ny = (ball_y - center_y) / dist

            dot = ball_dx * nx + ball_dy * ny
            ball_dx -= 2 * dot * nx
            ball_dy -= 2 * dot * ny

            ball_dx *= restitution
            ball_dy *= restitution

            overlap = (dist + ball_radius) - circle_radius
            ball_x -= nx * overlap
            ball_y -= ny * overlap

            # Qui la pallina si ingrandisce
            ball_radius += 1.7 * scale
            bounced = True

            # Attiva glow
            circle_glow_time = pygame.time.get_ticks()

        hue = (hue + 10) % 360
        border_color = hsv_to_rgb(hue, 1, 1)

        # Scia
        steps = 1
        for i in range(steps):
            t = i / steps
            interp_x = old_ball_x + (ball_x - old_ball_x) * t
            interp_y = old_ball_y + (ball_y - old_ball_y) * t
            pygame.draw.circle(trail_surface, BLACK, (int(interp_x), int(interp_y)), int(ball_radius))
            pygame.draw.circle(trail_surface, border_color, (int(interp_x), int(interp_y)), int(ball_radius), 1)

        # Suono rimbalzo
        if bounced:
            bounce_sound.play()

    else:
        hue = (hue + 10) % 360
        border_color = hsv_to_rgb(hue, 1, 1)

    # Sfondo
    screen.fill(BLACK)

    # Cerchio pieno bianco
    pygame.draw.circle(screen, WHITE, (center_x, center_y), circle_radius)

    # Glow sfumato attorno al bordo
    if circle_glow_time is not None:
        elapsed = (pygame.time.get_ticks() - circle_glow_time) / 1000
        if elapsed <= circle_glow_duration:
            fade = 1 - (elapsed / circle_glow_duration)
            max_glow_width = int(20 * scale)
            steps = 5
            for i in range(steps):
                alpha = int(120 * fade * (1 - i / steps))
                radius = circle_radius + i * (max_glow_width // steps)
                glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surface,
                    (255, 255, 0, alpha),
                    (radius, radius),
                    radius,
                    max(1, int(5 * scale))
                )
                screen.blit(glow_surface, (center_x - radius, center_y - radius))
        else:
            circle_glow_time = None

    # Scia
    screen.blit(trail_surface, (0, 0))

    # Pallina
    pygame.draw.circle(screen, BLACK, (int(ball_x), int(ball_y)), int(ball_radius))
    pygame.draw.circle(screen, border_color, (int(ball_x), int(ball_y)), int(ball_radius), max(1, int(scale)))

    pygame.display.flip()

pygame.quit()