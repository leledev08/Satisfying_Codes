import pygame
import random
import math
import colorsys

pygame.init()

# Carica suono ping (metti ping.mp3 nella cartella del progetto)
try:
    ping_sound = pygame.mixer.Sound("assets/sounds/ping.mp3")
    ping_sound.set_volume(1.0)  # volume massimo
except pygame.error:
    ping_sound = None
    print("Attenzione: file ping.mp3 non trovato o errore nel caricamento.")

# Finestra ridimensionabile
screen = pygame.display.set_mode((1080, 1920))
pygame.display.set_caption("Palline - rimbalzo con suono e gravità")

# Colori sfondo e bordo
LIGHT_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Parametri
BORDER_RATIO = 0.0125           # Spessore bordo relativo al raggio
INITIAL_SPEED = 4.5             # Velocità iniziale pallina
INITIAL_RADIUS_RATIO = 0.008    # Pallina piccola (relativa)
MAX_BALLS = None                # Nessun limite palline
RANDOM_BOUNCE_ANGLE = math.radians(60)  # apertura angolo rimbalzo
BALL_BORDER_WIDTH_RATIO = 0.25   # Spessore bordo pallina relativo al raggio
GRAVITY = 0.01                 # Gravità verso il basso leggera

clock = pygame.time.Clock()

class Ball:
    def __init__(self, x, y, dx, dy, radius):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius

    def update(self, center, inner_radius):
        """Aggiorna posizione, applica gravità e gestisce rimbalzo sul bordo."""
        # Applica gravità sulla velocità verticale
        self.dy += GRAVITY

        self.x += self.dx
        self.y += self.dy

        vx = self.x - center[0]
        vy = self.y - center[1]
        dist = math.hypot(vx, vy)

        if dist == 0:
            nx, ny = 1.0, 0.0
        else:
            nx, ny = vx / dist, vy / dist

        penetration = dist + self.radius - inner_radius
        if penetration > 0:
            self.x -= nx * penetration
            self.y -= ny * penetration
            dot = self.dx * nx + self.dy * ny
            self.dx -= 2 * dot * nx
            self.dy -= 2 * dot * ny
            return True, nx, ny  # restituisce se rimbalzato + normale
        return False, None, None

    def color_from_position(self, center, inner_radius):
        """Colore graduale in base alla posizione (angolo + distanza)."""
        vx = self.x - center[0]
        vy = self.y - center[1]
        dist = math.hypot(vx, vy)
        angle = math.atan2(vy, vx)
        hue = (angle + math.pi) / (2 * math.pi)
        r_frac = min(dist / max(inner_radius, 1e-6), 1.0)
        saturation = 0.35 + 0.65 * r_frac
        value = 1.0 - 0.25 * r_frac
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))


def create_random_ball(center, base_radius):
    """Crea una pallina al centro con direzione casuale."""
    angle = random.uniform(0, 2 * math.pi)
    dx = INITIAL_SPEED * math.cos(angle)
    dy = INITIAL_SPEED * math.sin(angle)
    return Ball(center[0], center[1], dx, dy, base_radius)


# Inizializzazione
w, h = screen.get_size()
min_side = min(w, h)
ball_radius = max(2, int(min_side * INITIAL_RADIUS_RATIO))
center = (w // 2, h // 2)
balls = [create_random_ball(center, ball_radius)]

paused = True  # Parte fermo, attiva con space

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = False

    width, height = screen.get_size()
    min_side = min(width, height)
    center = (width // 2, height // 2)
    big_radius = int(min_side * 0.4)
    border_width = max(1, int(big_radius * BORDER_RATIO))
    inner_radius = big_radius - border_width
    ball_radius = max(2, int(min_side * INITIAL_RADIUS_RATIO))

    screen.fill(LIGHT_GRAY)
    pygame.draw.circle(screen, BLACK, center, big_radius)
    pygame.draw.circle(screen, WHITE, center, inner_radius)

    if not paused:
        new_balls = []
        for ball in balls:
            bounced, nx, ny = ball.update(center, inner_radius)
            if bounced:
                if ping_sound:
                    ping_sound.play()
                if MAX_BALLS is None or len(balls) + len(new_balls) < MAX_BALLS:
                    speed = math.hypot(ball.dx, ball.dy) or INITIAL_SPEED
                    radial_angle = math.atan2(-ny, -nx)
                    new_angle = radial_angle + random.uniform(-RANDOM_BOUNCE_ANGLE, RANDOM_BOUNCE_ANGLE)
                    ndx = speed * math.cos(new_angle)
                    ndy = speed * math.sin(new_angle)
                    nr = ball.radius
                    new_balls.append(Ball(ball.x, ball.y, ndx, ndy, nr))

            color = ball.color_from_position(center, inner_radius)
            border_w = max(1, int(ball.radius * BALL_BORDER_WIDTH_RATIO))
            pygame.draw.circle(screen, BLACK, (int(ball.x), int(ball.y)), ball.radius + border_w)
            pygame.draw.circle(screen, color, (int(ball.x), int(ball.y)), ball.radius)

        if new_balls:
            balls.extend(new_balls)
    else:
        # Disegna palline ferme senza aggiornare
        for ball in balls:
            color = ball.color_from_position(center, inner_radius)
            border_w = max(1, int(ball.radius * BALL_BORDER_WIDTH_RATIO))
            pygame.draw.circle(screen, BLACK, (int(ball.x), int(ball.y)), ball.radius + border_w)
            pygame.draw.circle(screen, color, (int(ball.x), int(ball.y)), ball.radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
