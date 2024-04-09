import pygame
import math
import numpy as np
import graphischedarsetllung as Gr
from spannung_steuerun import Steuerung
from robot_Modell import Modell
from ball_Modell import Ball
import matplotlib.pyplot as plt

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


# --- Pygame Initialization and configuration ---

pygame.init()
clock = pygame.time.Clock()
screen = Gr.screen
WIDTH, HEIGHT = Gr.WIDTH, Gr.HEIGHT  
pixel_scale = Gr.SCALE_FACTOR  

# Defining visual parameters for the ball and robot 
ball_radius = 25 * pixel_scale
robot_width = 105 * pixel_scale
robot_height = 150 * pixel_scale
robot_image = Gr.init_robot_image(robot_height, robot_width) 
robot_x, robot_y = (HEIGHT // 2)+50, (WIDTH // 2)  
V_max = 9  # Maximum voltage in volts
t_final=35 # Simulation duration (in seconds)
dt = 0.05 # Time step for the simulation

# Initial velocity of the ball in the x and y directions in m/s

v0=2
winkel_b = math.pi/3
Ball_vx0=v0 * np.cos(winkel_b)
Ball_vy0=v0 * np.sin(winkel_b)
# Conversion of the ball velocity
Ball_vx = geschwindigkeit_umrechnen(Ball_vx0)
Ball_vy = geschwindigkeit_umrechnen(Ball_vy0)

# Creating model, ball, and controller
model = Modell()
ball = Ball(HEIGHT // 2, WIDTH // 2, Ball_vx, Ball_vy)
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
#Pygame loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Checking for window closure
            running = False
    

       
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
        Gr.update_robot(Gr.screen, robot_image, robot_x, robot_y, winkel[i]) # Contains only rotating (must change)

    # Updating the positions
        robot_x += geschwindigkeit_umrechnen(speed[i]) *dt * np.cos(np.radians(winkel[i]))
        robot_y -= geschwindigkeit_umrechnen(speed[i]) *dt *np.sin(np.radians(winkel[i]))

        ball.ball_bewegung(dt, ball_radius, HEIGHT, WIDTH,winkel_b)
        ball.ball_wand_kollision_x(HEIGHT, ball_radius )
        ball.ball_wand_kollision_y(WIDTH, ball_radius )

        
        
        
       
    # Collision detection and response
        robot_vx = geschwindigkeit_umrechnen(speed[i]) *dt * np.cos(np.radians(winkel[i]))
        robot_vy = -geschwindigkeit_umrechnen(speed[i]) *dt * np.sin(np.radians(winkel[i]))
        ball.kollision_detektion(dt, ball_radius, robot_x, robot_y, robot_width, robot_height, winkel[i], robot_vx, robot_vy)
     
    # Calculating the ball's velocity 
        ball_speed_px_s = np.sqrt(ball.geschwindigkeit[0]**2 + ball.geschwindigkeit[1]**2)
        ball_speed_m_s = pixelgeschwindigkeit_umrechnen(ball_speed_px_s)

        # Display velocities of ball and robot on the screen

        ball_text = font.render(f"Velocity of the ball: {ball_speed_m_s:.2f} m/s", True, Gr.RED)
        robot_text = font.render(f"Velocity of the robot: {np.absolute(speed[i]):.2f} m/s", True, Gr.RED)
        ball_position = (10, 30)
        speed_position = (10, 50)
        screen.blit(ball_text, ball_position)
        screen.blit(robot_text, speed_position)

        pygame.display.flip()  # Updating Displays
        pygame.time.delay(30)  # Pause to slow down the loop
        i += 1
    else:
        running==False
        pass

    # Regulate the frames per second
    clock.tick(60)
# Exiting Pygame
pygame.quit()