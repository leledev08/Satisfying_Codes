import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Create a window
WIDGHT, HEIGHT = 1422, 800
screen_center = [WIDGHT // 2, HEIGHT // 2]
screen = pygame.display.set_mode((WIDGHT, HEIGHT))
pygame.display.set_caption("Video 6")

# Border parameters
border_radius = 350
border_outline_width = 5

# Gravity
GRAVITY = 0.25

# Ball parameters
ball_radius = 15
ball_outline_width = 5
ball_pos = screen_center.copy()
ball_color = pygame.Color(255, 255, 255)
ball_velocity = [+3, -8]
ball_acceleration = [0, GRAVITY]

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update ball position
    ball_velocity[0] += ball_acceleration[0]
    ball_velocity[1] += ball_acceleration[1]
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]

    # Calculate distance between ball and center of border
    dx = ball_pos[0] - screen_center[0]
    dy = ball_pos[1] - screen_center[1]
    distance_from_center = math.sqrt(dx**2 + dy**2)

    # Check for collision with border
    if distance_from_center >= border_radius - ball_radius:
        normal = [dx / distance_from_center, dy / distance_from_center]
        dot_product = (ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1])
        reflection = [ball_velocity[0] - 2 * dot_product * normal[0],
                      ball_velocity[1] - 2 * dot_product * normal[1]]
        ball_velocity = [reflection[0], reflection[1]]
        # Move ball to the edge of the border
        ball_pos[0] = screen_center[0] + normal[0] * (border_radius - ball_radius)
        ball_pos[1] = screen_center[1] + normal[1] * (border_radius - ball_radius)

    # Clear the screen
    screen.fill((0, 0, 0))

    #Draw border
    pygame.draw.circle(screen, (255, 255, 255), (screen_center[0], screen_center[1]), border_radius + border_outline_width)
    pygame.draw.circle(screen, (0, 0, 0), (screen_center[0], screen_center[1]), border_radius)

    # Draw ball
    ball_color.hsva = (0, 100, 40, 100)
    pygame.draw.circle(screen, ball_color, (ball_pos[0], ball_pos[1]), ball_radius + ball_outline_width)
    ball_color.hsva = (0, 100, 90, 100)
    pygame.draw.circle(screen, ball_color, (ball_pos[0], ball_pos[1]), ball_radius)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(120)