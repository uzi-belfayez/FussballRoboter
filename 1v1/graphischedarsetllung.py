import pygame

# Constants for screen size and scaling factor.
SCALE_FACTOR = 0.5# 100 pixels correspond to 200 millimeters.
WIDTH = int(1220 * SCALE_FACTOR)  # Conversion of real dimensions into pixels.
HEIGHT = int(1830 * SCALE_FACTOR)

# Color definitions
BLACK = (0, 0, 0)
WOOD = (210, 180, 140)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((HEIGHT, WIDTH))  # Set window size
pygame.display.set_caption("Fußballfeld")  # Set window title

def draw_field_background():
    # Draws the background of the game field
    screen.fill(BLACK)  # Fills the entire screen with black.
    # Draws the game field in wood color.
    pygame.draw.rect(screen, WOOD, [SCALE_FACTOR*10, SCALE_FACTOR*10, HEIGHT-SCALE_FACTOR*20, WIDTH-SCALE_FACTOR*20])

def draw_lines():
    # Draws the lines of the game field
    pygame.draw.rect(screen, BLACK, [0, 0, HEIGHT, WIDTH], int(SCALE_FACTOR*10))  # Border around the game field
    
    # Drawing the horizontal lines
    lines_horizontal = [
        HEIGHT // 2, HEIGHT // 2 - int(350*SCALE_FACTOR), 
        HEIGHT // 2 - int(700*SCALE_FACTOR), HEIGHT // 2 + int(350*SCALE_FACTOR), 
        HEIGHT // 2 + int(700*SCALE_FACTOR)
    ]
    # Iterating over the defined lines and drawing them on the screen
    for line in lines_horizontal:
        pygame.draw.line(screen, YELLOW, (line, SCALE_FACTOR*10), (line, WIDTH - SCALE_FACTOR*10), int(SCALE_FACTOR*20))

    # Drawing the vertical lines
    lines_vertical = [WIDTH // 2, WIDTH // 2 - int(350*SCALE_FACTOR), WIDTH // 2 + int(350*SCALE_FACTOR)]
    # Iterating and drawing the vertical lines
    for line in lines_vertical:
        pygame.draw.line(screen, BLACK, (SCALE_FACTOR*10, line), (HEIGHT - SCALE_FACTOR*10, line), int(SCALE_FACTOR*20))

def draw_goals():
    # Draws the goals
    goal_width = int(10 * SCALE_FACTOR)
    goal_height = int(350 * SCALE_FACTOR)
    left_goal_x = 0
    right_goal_x = HEIGHT - goal_width
    goal_y = (WIDTH - goal_height) // 2
    
    # Drawing the goals on both sides of the game field
    pygame.draw.rect(screen, GREEN, [left_goal_x, goal_y, goal_width, goal_height])
    pygame.draw.rect(screen, GREEN, [right_goal_x , goal_y, goal_width, goal_height])

def draw_field():
    # Function to draw the entire game field
    draw_field_background()  
    draw_lines()  
    draw_goals()  

def draw_ball(screen, ball, ball_radius, color):
    pygame.draw.circle(screen, color, ball.position, ball_radius)

def init_robot_image(robot_height, robot_width):
    # Function to initialize the robot image and scale it to the desired size
    robot_image = pygame.image.load("robot.png")
    return pygame.transform.scale(robot_image, (robot_height, robot_width))  



def init_robot1_image(robot_height, robot_width):
    # Function to initialize the robot image and scale it to the desired size
    robot_image = pygame.image.load("robot1.png")
    return pygame.transform.scale(robot_image, (robot_height, robot_width))


def update_robot(screen, robot_image, robot_x, robot_y, winkel):
    # Function to update the robot on the screen
    robot_rotated = pygame.transform.rotate(robot_image, winkel)  # Rotating the robot image by the angle
    # Creating a rectangle around the rotated image to manage position and collisions
    robot_rect = robot_rotated.get_rect(center=(robot_x, robot_y))
    # Calculating the coordinates of the upper left corner for positioning the rotated image
    robot_x_topleft = robot_rect.centerx - robot_rect.width // 2
    robot_y_topleft = robot_rect.centery - robot_rect.height // 2
    # Drawing the rotated image at the calculated position on the screen
    screen.blit(robot_rotated, (robot_x_topleft, robot_y_topleft))