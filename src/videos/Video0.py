import pygame
import math
import random
import colorsys

pygame.init()
pygame.mixer.init()

# Schermo e parametri principali per TikTok
WIDTH, HEIGHT = 1080, 1920
CENTER = (WIDTH // 2, HEIGHT // 2)
RADIUS = 450
OPENING_DEG = 37
OPENING_RAD = math.radians(OPENING_DEG)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

GRAVITY = 0.6

# Suoni
ping_sound = pygame.mixer.Sound("assets/sounds/pingpong.mp3")
pop_sound = pygame.mixer.Sound("assets/sounds/pop.mp3")

# Tavolozza colori brillanti
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

def angle_from_center(pos):
    dx = pos[0] - CENTER[0]
    dy = pos[1] - CENTER[1]
    angle = math.atan2(dy, dx)
    if angle < 0:
        angle += 2 * math.pi
    return angle

def random_bright_color():
    return random.choice(bright_colors)

def in_arc(angle, start, end):
    if start < end:
        return start <= angle <= end
    else:
        return angle >= start or angle <= end

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(2, 4)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1
    
    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, int(255 * (self.life / 40)))
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.radius, self.radius), self.radius)
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))

class Ball:
    def __init__(self):
        inside = False
        while not inside:
            # y random tra -200 e la parte superiore del cerchio
            y_offset = random.uniform(-RADIUS, -200)
            # distanza massima in x consentita per rimanere nel cerchio
            max_dx = math.sqrt(RADIUS**2 - y_offset**2)
            x_offset = random.uniform(-max_dx, max_dx)
            
            self.x = CENTER[0] + x_offset
            self.y = CENTER[1] + y_offset
            
            # controllo sicurezza
            dx = self.x - CENTER[0]
            dy = self.y - CENTER[1]
            if math.hypot(dx, dy) + 12 <= RADIUS:  # 12 = raggio palla
                inside = True

        # velocità
        speed = 8
        angle_v = random.uniform(0, 2*math.pi)
        self.vx = speed * math.cos(angle_v)
        self.vy = speed * math.sin(angle_v)
        
        self.radius = 12
        self.color = random_bright_color()
        self.outside = False


    def update(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        
        dx = self.x - CENTER[0]
        dy = self.y - CENTER[1]
        dist = math.hypot(dx, dy)
        
        ang = angle_from_center((self.x, self.y))
        
        start_open = (rotation_angle - OPENING_RAD/2) % (2*math.pi)
        end_open = (rotation_angle + OPENING_RAD/2) % (2*math.pi)
        
        in_opening = in_arc(ang, start_open, end_open)
        
        if dist + self.radius > RADIUS:
            if in_opening:
                self.outside = True
                pop_sound.play()
            else:
                # Rimbalzo
                nx = dx / dist
                ny = dy / dist
                dot = self.vx * nx + self.vy * ny
                self.vx -= 2 * dot * nx
                self.vy -= 2 * dot * ny
                
                overlap = dist + self.radius - RADIUS
                self.x -= nx * overlap
                self.y -= ny * overlap
                
                ping_sound.play()
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

def draw_colored_circle(surface, center, radius, rotation_angle, opening_rad, time_var):
    segs = 720
    thick = 4
    hue = (0.57 + time_var * 0.0003) % 1.0
    saturation = 0.75
    lightness = 0.75
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    fixed_color = (int(r*255), int(g*255), int(b*255))

    for i in range(segs):
        sa = (2*math.pi / segs) * i
        ea = (2*math.pi / segs) * (i + 1)
        mid = (sa + ea) / 2
        if in_arc(mid, (rotation_angle - opening_rad/2) % (2*math.pi), 
                  (rotation_angle + opening_rad/2) % (2*math.pi)):
            continue
        pygame.draw.arc(surface, fixed_color,
                        pygame.Rect(center[0]-radius, center[1]-radius, radius*2, radius*2),
                        -ea, -sa, thick)

def draw_black_opening(surface, center, radius, rotation_angle, opening_rad):
    steps = 30
    start_angle = (rotation_angle - opening_rad/2) % (2*math.pi)
    points = [center]
    for i in range(steps+1):
        angle = start_angle + i * (opening_rad / steps)
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(surface, BLACK, points)

def main():
    global rotation_angle
    balls = [Ball()]
    particles = []
    running = True
    rotation_angle = 0
    rotation_speed = math.radians(1.5)
    paused = True
    frame_count = 0
    
    while running:
        clock.tick(60)
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
        
        if not paused:
            frame_count += 1  # Avanza solo se in gioco
            rotation_angle -= rotation_speed
            rotation_angle %= 2*math.pi
            
            draw_colored_circle(screen, CENTER, RADIUS, rotation_angle, OPENING_RAD, frame_count)
            draw_black_opening(screen, CENTER, RADIUS, rotation_angle, OPENING_RAD)
            
            new_balls = []
            remaining_balls = []
            
            for ball in balls:
                ball.update()
                ball.draw(screen)
                
                if ball.outside:
                    for _ in range(20):
                        particles.append(Particle(ball.x, ball.y, ball.color))
                    new_balls.append(Ball())
                    new_balls.append(Ball())
                else:
                    remaining_balls.append(ball)
            
            balls = remaining_balls + new_balls
            
            for p in particles[:]:
                p.update()
                p.draw(screen)
                if p.life <= 0:
                    particles.remove(p)
        
        else:
            draw_colored_circle(screen, CENTER, RADIUS, rotation_angle, OPENING_RAD, frame_count)
            draw_black_opening(screen, CENTER, RADIUS, rotation_angle, OPENING_RAD)
            for ball in balls:
                ball.draw(screen)
            for p in particles:
                p.draw(screen)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
