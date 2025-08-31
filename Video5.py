import pygame
import math
import random
import colorsys

pygame.init()

# --- Schermo 1080x1920 (9:16) ---
WIDTH, HEIGHT = 1080, 1920
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Video 5")

# --- Colori e costanti ---
BLACK = (0, 0, 0)
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
OUTER_RADIUS = 505
INITIAL_OUTER_THICKNESS = 5

GRAVITY = 1.1
GROWTH_PER_BOUNCE = 25
RING_THICKNESS = 25
MAX_ITERATIONS = 20
PUSH_TO_CENTER = 1.6

# --- Suoni ---
ping_sound = pygame.mixer.Sound("assets/sounds/pingpong.mp3")
pop_sound = pygame.mixer.Sound("assets/sounds/pop.mp3")

# --- Glow ---
circle_glow_time = None
circle_glow_duration = 0.4  # secondi

def gradient_color(i, total):
    hue = (i / max(total - 1, 1)) * 0.75
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    return (int(r*255), int(g*255), int(b*255))

def reset_ring():
    global x, y, vx, vy, ring_radius, ring_color, last_bounce_dist
    x, y = CENTER_X, CENTER_Y
    ring_radius = RING_THICKNESS
    ang = random.uniform(0, 2 * math.pi)
    speed = 15
    vx = math.cos(ang) * speed
    vy = math.sin(ang) * speed
    ring_color = gradient_color(iteration, MAX_ITERATIONS)
    last_bounce_dist = 0

# --- Setup iniziale ---
border_segments = [(INITIAL_OUTER_THICKNESS, (255, 255, 255))]
iteration = 0
reset_ring()

clock = pygame.time.Clock()
running = True
paused = True  # parte fermo

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = False

    if not paused:
        # Movimento e gravità
        vy += GRAVITY
        x += vx
        y += vy

        dx = x - CENTER_X
        dy = y - CENTER_Y
        dist = math.hypot(dx, dy)
        limit_radius = OUTER_RADIUS - sum(t for t, _ in border_segments)
        bounced = False

        # Controllo rimbalzo
        if dist + ring_radius >= limit_radius:
            nx, ny = dx / dist, dy / dist
            dot = vx * nx + vy * ny
            vx -= 2 * dot * nx
            vy -= 2 * dot * ny

            overlap = (dist + ring_radius) - limit_radius
            x -= nx * overlap
            y -= ny * overlap

            vx -= nx * PUSH_TO_CENTER
            vy -= ny * PUSH_TO_CENTER

            ping_sound.play()
            last_bounce_dist = dist
            bounced = True
            circle_glow_time = pygame.time.get_ticks()  # glow

        # Crescita dopo allontanamento
        if last_bounce_dist is not None:
            if dist <= last_bounce_dist - GROWTH_PER_BOUNCE:
                ring_radius += GROWTH_PER_BOUNCE
                last_bounce_dist = None

                if ring_radius >= limit_radius:
                    ring_radius = limit_radius
                    vx, vy = 0, 0
                    pop_sound.play()
                    border_segments.append((RING_THICKNESS, ring_color))
                    iteration += 1
                    if iteration >= MAX_ITERATIONS:
                        running = False
                    else:
                        reset_ring()

    # Disegno
    screen.fill(BLACK)
    current_radius = OUTER_RADIUS
    for thickness, color in border_segments:
        # Cerchio bianco esterno con glow
        if color == (255, 255, 255):
            if circle_glow_time is not None:
                elapsed = (pygame.time.get_ticks() - circle_glow_time) / 1000
                if elapsed <= circle_glow_duration:
                    fade = 1 - (elapsed / circle_glow_duration)
                    max_glow_width = 20
                    steps = 10
                    for i in range(steps):
                        alpha = int(120 * fade * (1 - i / steps))
                        radius = current_radius + i * (max_glow_width // steps)
                        glow_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surface, (255, 255, 0, alpha), (radius, radius), radius, 3)
                        screen.blit(glow_surface, (CENTER_X - radius, CENTER_Y - radius))
                else:
                    circle_glow_time = None
        pygame.draw.circle(screen, color, (CENTER_X, CENTER_Y), int(current_radius), int(thickness))
        current_radius -= thickness

    pygame.draw.circle(screen, ring_color, (int(x), int(y)), int(ring_radius), RING_THICKNESS)

    pygame.display.flip()

pygame.quit()
