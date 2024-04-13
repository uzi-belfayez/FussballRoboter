import pygame
import math
import numpy as np
import graphischedarsetllung as Gr
from spannung_steuerun import Steuerung
from robot_Modell import Modell
from ball_Modell import Ball
import matplotlib.pyplot as plt
from enum import Enum



class Direction(Enum):
    STRAIGHT = 1
    RIGHT = 2
    LEFT = 3

"""Converting velocity from m/s to pixels/s."""
def geschwindigkeit_umrechnen(geschwindigkeit_m_s):
    geschwindigkeit_mm_s = geschwindigkeit_m_s * 1000  # Conversion of meters to millimeters.
    geschwindigkeit_pixel_s = geschwindigkeit_mm_s * 0.2  # Application of the scaling factor 
    return geschwindigkeit_pixel_s

"""Converting velocity from pixels/s to m/s."""
def pixelgeschwindigkeit_umrechnen(geschwindigkeit_pixel_s):
    geschwindigkeit_mm_s = geschwindigkeit_pixel_s / 0.2  
    geschwindigkeit_m_s = geschwindigkeit_mm_s / 1000  
    return geschwindigkeit_m_s

def reset(i):
    robot_x, robot_y = (HEIGHT // 2)+50, (WIDTH // 2)
    ball.reset()
    i = 0


def _move(direction):
    
    if direction == Direction.STRAIGHT:
        current_speed += 0.1
        if abs(current_speed)>=0.8:
            current_speed=math.copysign(2,current_speed)
    if direction == Direction.RIGHT:
        current_angle += 4
    if direction == Direction.LEFT:
        current_angle -= 4

    current_angle%=360

    return current_angle, current_speed

frame_iteration = 0

def play_step(action, frame_iteration):
    frame_iteration += 1
    reward = 0
    game_over = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    current_angle, current_speed = _move(action)

    robot_x += geschwindigkeit_umrechnen(current_speed) *dt * np.cos(np.radians(current_angle))
    robot_y -= geschwindigkeit_umrechnen(current_speed) *dt *np.sin(np.radians(current_angle))

    if frame_iteration > 1000*(ball.right_team_score+ball.left_team_score):
        game_over = True
        reward = -10
        return reward, game_over
    
    if ball.right_goal_scored:    
        reward = 100
        return reward, game_over
    if ball.left_goal_scored:
        reward = -100
        return reward, game_over
    if ball.robot_ball_kollision:
        reward = 10
        return reward, game_over

def update_ui():

    screen.fill(Gr.BLACK)
    if i < len(time_data):
        screen.fill(Gr.BLACK)
    # Drawing the game field
        Gr.draw_field()
    # Drawing the ball
        Gr.draw_ball(Gr.screen, ball, ball_radius, Gr.GREEN)     
    # Updating the positions
        robot_x += geschwindigkeit_umrechnen(current_speed) *dt * np.cos(np.radians(current_angle))
        robot_y -= geschwindigkeit_umrechnen(current_speed) *dt *np.sin(np.radians(current_angle))

    # Reseting the robot position after a goal
        if ball.right_goal_scored or ball.left_goal_scored:
            robot_x, robot_y = (HEIGHT // 2)+50, (WIDTH // 2)
            current_angle = 0
            ball.right_goal_scored = False
            ball.left_goal_scored = False


    # Updating the ball position
        ball.ball_bewegung(dt, ball_radius, HEIGHT, WIDTH,winkel_b)
        ball.ball_wand_kollision_x(HEIGHT, ball_radius )
        ball.ball_wand_kollision_y(WIDTH, ball_radius )
 
    # Collision detection and response
        robot_vx = geschwindigkeit_umrechnen(current_speed) *dt * np.cos(np.radians(current_angle))
        robot_vy = -geschwindigkeit_umrechnen(current_speed) *dt * np.sin(np.radians(current_angle))
        ball.kollision_detektion(dt, ball_radius, robot_x, robot_y, robot_width, robot_height, current_angle, 10*robot_vx, 10*robot_vy)
    
    # Score goal
        ball.score_goal(910,0,217,175,5,ball_radius)

    # Calculating the ball's velocity 
        ball_speed_px_s = np.sqrt(ball.geschwindigkeit[0]**2 + ball.geschwindigkeit[1]**2)
        ball_speed_m_s = pixelgeschwindigkeit_umrechnen(ball_speed_px_s)

    # Display velocities of ball and robot on the screen

    ball_text = font.render(f"Velocity of the ball: {ball_speed_m_s:.2f} m/s", True, Gr.RED)
    robot_text = font.render(f"Velocity of the robot: {np.absolute(current_speed):.2f} m/s", True, Gr.RED)
    ball_position = (10, 30)
    speed_position = (10, 50)
    screen.blit(ball_text, ball_position)
    screen.blit(robot_text, speed_position)
    
    #display score 
    score_text = font.render(f"Right team score: {ball.right_team_score} Left team score: {ball.left_team_score}", True, Gr.RED)
    score_position = (10, 70)
    screen.blit(score_text, score_position)

    #display the ball coordinates
    ball_coordinates = font.render(f"Ball coordinates: ({round(ball.position[0])},{round(ball.position[1])})", True, Gr.RED)
    ball_coordinates_position = (10, 90)
    screen.blit(ball_coordinates, ball_coordinates_position)



    pygame.display.flip()  # Updating Displays
    pygame.time.delay(30) # Pause to slow down the loop
    



# --- Pygame Initialization and configuration ---

pygame.init()
clock = pygame.time.Clock()
screen = Gr.screen
WIDTH, HEIGHT = Gr.WIDTH, Gr.HEIGHT  
pixel_scale = Gr.SCALE_FACTOR  

# Defining visual parameters for the ball and robot 
ball_radius = 25 * pixel_scale
robot_width = 125 * pixel_scale
robot_height = 150 * pixel_scale
robot_image = Gr.init_robot_image(robot_height, robot_width) 
robot_x, robot_y = (HEIGHT // 2)+50, (WIDTH // 2)  
V_max = 9  # Maximum voltage in volts
t_final=10 # Simulation duration (in seconds)
dt = 0.05 # Time step for the simulation

# Initial velocity of the ball in the x and y directions in m/s

v0=0
winkel_b = 0
Ball_vx0=v0 * np.cos(winkel_b)
Ball_vy0=v0 * np.sin(winkel_b)
# Conversion of the ball velocity
Ball_vx = geschwindigkeit_umrechnen(Ball_vx0)
Ball_vy = geschwindigkeit_umrechnen(Ball_vy0)

# Creating model, ball, and controller
model = Modell()
#ball = Ball(HEIGHT // 2, WIDTH // 2, Ball_vx, Ball_vy)
ball = Ball(HEIGHT // 2, WIDTH // 2, 0, 0,HEIGHT // 2, WIDTH // 2)
steuerung=Steuerung(0,t_final,V_max)
# Retrieve various robot data from the robot model
time, speed, w_right, w_left,v_left,v_right, x, y ,winkel,accel= model.simulate(steuerung.recht,steuerung.link)

# Defining the font for text output
font = pygame.font.SysFont("Roboto", 20)
clock = pygame.time.Clock()
time_data = time



# --- Main event loop ---
i = 0  # Index for time-dependent variables
running = True
current_angle = 0
current_speed = 0
key_state = {}
keys = {pygame.K_UP:"K_UP",
        pygame.K_DOWN:"K_DOWN",
        pygame.K_RIGHT:"K_RIGHT",
        pygame.K_LEFT:"K_LEFT"
        }
#Pygame loop
while running:
    
            
    
    # Graphics
    # Fill screen background
    screen.fill(Gr.BLACK)
    if i < len(time_data):
        screen.fill(Gr.BLACK)
    # Drawing the game field
        Gr.draw_field()
    # Drawing the ball
        Gr.draw_ball(Gr.screen, ball, ball_radius, Gr.GREEN)     
    # Updating and drawing the robot
        Gr.update_robot(Gr.screen, robot_image, robot_x, robot_y, current_angle) # Contains only rotating (must change)
    # Updating the positions
        robot_x += geschwindigkeit_umrechnen(current_speed) *dt * np.cos(np.radians(current_angle))
        robot_y -= geschwindigkeit_umrechnen(current_speed) *dt *np.sin(np.radians(current_angle))

    # Reseting the robot position after a goal
        if ball.right_goal_scored or ball.left_goal_scored:
            robot_x, robot_y = (HEIGHT // 2)+50, (WIDTH // 2)
            current_angle = 0
            ball.right_goal_scored = False
            ball.left_goal_scored = False


    # Updating the ball position
        ball.ball_bewegung(dt, ball_radius, HEIGHT, WIDTH,winkel_b)
        ball.ball_wand_kollision_x(HEIGHT, ball_radius )
        ball.ball_wand_kollision_y(WIDTH, ball_radius )

        
        
        
       
    # Collision detection and response
        robot_vx = geschwindigkeit_umrechnen(current_speed) *dt * np.cos(np.radians(current_angle))
        robot_vy = -geschwindigkeit_umrechnen(current_speed) *dt * np.sin(np.radians(current_angle))
        ball.kollision_detektion(dt, ball_radius, robot_x, robot_y, robot_width, robot_height, current_angle, 10*robot_vx, 10*robot_vy)
    
    # Score goal
        ball.score_goal(910,0,217,175,5,ball_radius)



    # Calculating the ball's velocity 
        ball_speed_px_s = np.sqrt(ball.geschwindigkeit[0]**2 + ball.geschwindigkeit[1]**2)
        ball_speed_m_s = pixelgeschwindigkeit_umrechnen(ball_speed_px_s)

    else:
        reset(i)

    # Display velocities of ball and robot on the screen

    ball_text = font.render(f"Velocity of the ball: {ball_speed_m_s:.2f} m/s", True, Gr.RED)
    robot_text = font.render(f"Velocity of the robot: {np.absolute(current_speed):.2f} m/s", True, Gr.RED)
    ball_position = (10, 30)
    speed_position = (10, 50)
    screen.blit(ball_text, ball_position)
    screen.blit(robot_text, speed_position)
    
    #display score 
    score_text = font.render(f"Right team score: {ball.right_team_score} Left team score: {ball.left_team_score}", True, Gr.RED)
    score_position = (10, 70)
    screen.blit(score_text, score_position)

    #display the ball coordinates
    ball_coordinates = font.render(f"Ball coordinates: ({round(ball.position[0])},{round(ball.position[1])})", True, Gr.RED)
    ball_coordinates_position = (10, 90)
    screen.blit(ball_coordinates, ball_coordinates_position)



    pygame.display.flip()  # Updating Displays
    pygame.time.delay(30)  # Pause to slow down the loop
        
    

    # Regulate the frames per second
    clock.tick(60)
# Exiting Pygame
pygame.quit()