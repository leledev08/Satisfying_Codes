import pygame
import colorsys
import math

pygame.init()

# --- Schermo ---
WIDTH, HEIGHT = 1080, 1920
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Video 4")

# --- Colori e costanti ---
BLACK = (0, 0, 0)
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
OUTER_RADIUS = 450
INNER_RADIUS = 110
RING_THICKNESS = 12
BALL_RADIUS = 30
GRAVITY = 0.5

# --- Cerchi concentrici ---
NUM_RINGS = (OUTER_RADIUS - INNER_RADIUS) // RING_THICKNESS

def rainbow_colors(n):
    colors = []
    for i in range(n):
        hue = i / max(n-1,1) * 0.75
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        colors.append((int(r*255), int(g*255), int(b*255)))
    return colors

fixed_ring_colors = rainbow_colors(NUM_RINGS)
active_layers = NUM_RINGS  # inizialmente tutti

# --- Pallina ---
ball_x, ball_y = CENTER_X, CENTER_Y
ball_vx, ball_vy = 4, 7
hue = 0

# Velocità graduale
speed_increase_factor = 1.001201

# Scia
trail_length = 50
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
trail_positions = []

# Suono layer
pygame.mixer.init()
layer_sound = pygame.mixer.Sound("assets/sounds/pingpong.mp3")

# Timer per aggiungere cerchi
add_cooldown = 300  # millisecondi
last_add_time = 0  # ultima volta che un cerchio è stato aggiunto

def compute_hitboxes():
    hitboxes = []
    current_radius = OUTER_RADIUS
    for _ in range(active_layers):
        hitboxes.append((current_radius - RING_THICKNESS, current_radius))
        current_radius -= RING_THICKNESS
    return hitboxes

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
    return int(r*255), int(g*255), int(b*255)

ring_hitboxes = compute_hitboxes()
clock = pygame.time.Clock()
running = True

paused = True  # Parte fermo

while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # Inverti stato pausa

    if not paused:
        old_ball_x, old_ball_y = ball_x, ball_y

        # Incremento graduale velocità
        ball_vx *= speed_increase_factor
        ball_vy *= speed_increase_factor

        # Aggiorna pallina
        ball_vy += GRAVITY
        ball_x += ball_vx
        ball_y += ball_vy

        # Aggiorna colore gradualmente
        hue = (hue + 2) % 360
        border_color = hsv_to_rgb(hue, 1, 1)

        # Distanza dal centro
        dx = ball_x - CENTER_X
        dy = ball_y - CENTER_Y
        distance = math.hypot(dx, dy)

        # Collisione con gli anelli
        for i, (r_inner, r_outer) in enumerate(ring_hitboxes):
            if r_inner - BALL_RADIUS < distance < r_outer + BALL_RADIUS:
                norm_dx = dx / distance
                norm_dy = dy / distance
                v_radial = ball_vx * norm_dx + ball_vy * norm_dy
                ball_vx -= 2 * v_radial * norm_dx
                ball_vy -= 2 * v_radial * norm_dy

                # Gestione layer
                layer_changed = False
                if ball_y < CENTER_Y:
                    if active_layers < NUM_RINGS and (current_time - last_add_time) >= add_cooldown:
                        active_layers += 1
                        last_add_time = current_time
                        layer_changed = True
                else:
                    if active_layers > 0:
                        active_layers -= 1
                        layer_changed = True

                if layer_changed:
                    layer_sound.play()

                ring_hitboxes = compute_hitboxes()

                # Sposta pallina fuori dall'anello
                if distance < r_inner:
                    distance = r_inner - BALL_RADIUS
                else:
                    distance = r_outer + BALL_RADIUS
                ball_x = CENTER_X + norm_dx * distance
                ball_y = CENTER_Y + norm_dy * distance

                break

        # Aggiungi posizione alla scia
        trail_positions.append((ball_x, ball_y, BALL_RADIUS, hue))
        if len(trail_positions) > trail_length:
            trail_positions.pop(0)

        # Ripulisci superficie scia
        trail_surface.fill((0,0,0,0))
        for i, (tx, ty, tr, th) in enumerate(trail_positions):
            alpha = int(255 * (i+1)/trail_length)
            color = hsv_to_rgb(th, 1, 1)
            pygame.draw.circle(trail_surface, (*color, alpha), (int(tx), int(ty)), int(tr), 1)

    # --- Disegno (sempre attivo, anche se in pausa) ---
    screen.fill(BLACK)

    # Disegniamo i cerchi concentrici
    current_radius = OUTER_RADIUS
    for i in range(active_layers):
        color = fixed_ring_colors[i]
        pygame.draw.circle(screen, color, (CENTER_X, CENTER_Y), int(current_radius), RING_THICKNESS)
        current_radius -= RING_THICKNESS

    pygame.draw.circle(screen, BLACK, (CENTER_X, CENTER_Y), INNER_RADIUS)

    # Creiamo superficie per la linea
    line_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    line_surface.fill((0,0,0,0))
    pygame.draw.line(line_surface, (255,255,255), (0, CENTER_Y), (WIDTH, CENTER_Y), 2)

    # Creiamo maschera dei layer
    layer_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    layer_mask.fill((0,0,0,0))
    current_radius = OUTER_RADIUS
    for i in range(active_layers):
        pygame.draw.circle(layer_mask, (255,255,255,255), (CENTER_X, CENTER_Y), int(current_radius), RING_THICKNESS)
        current_radius -= RING_THICKNESS

    # Applichiamo maschera alla linea
    line_surface.blit(layer_mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    screen.blit(line_surface, (0,0))

    # Disegniamo la scia e la pallina
    screen.blit(trail_surface, (0,0))
    pygame.draw.circle(screen, hsv_to_rgb(hue,1,1), (int(ball_x), int(ball_y)), BALL_RADIUS)
    pygame.draw.circle(screen, (255,255,255), (int(ball_x), int(ball_y)), BALL_RADIUS, 2)

    pygame.display.flip()

pygame.quit()
