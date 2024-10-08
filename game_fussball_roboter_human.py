import pygame
import math
import numpy as np
import graphischedarsetllung as Gr
from spannung_steuerun import Steuerung
from ball_Modell import Ball
import matplotlib.pyplot as plt
from enum import Enum

# --- Pygame Initialization and configuration ---
pygame.init()
font = pygame.font.SysFont("Roboto", 20)




class Direction(Enum):
    STRAIGHT = 1
    RIGHT = 2
    LEFT = 3
    NONE = 4

class fussball_roboter:
    def __init__(self) -> None:

        self.screen = Gr.screen
        self.WIDTH, self.HEIGHT = Gr.WIDTH, Gr.HEIGHT  
        self.pixel_scale = Gr.SCALE_FACTOR
        
        self.display = pygame.display.set_mode((self.HEIGHT, self.WIDTH))
        self.clock = pygame.time.Clock()

        self.direction = Direction.NONE


        # Defining visual parameters for the ball and robot 
        self.ball_radius = 25 *  self.pixel_scale
        self.robot_width = 125 * self.pixel_scale
        self.robot_height = 150 *self.pixel_scale
        self.robot_image = Gr.init_robot_image(self.robot_height, self.robot_width) 
        self.robot_x = (self.HEIGHT // 2)-50 
        self.robot_y = (self.WIDTH // 2)  
        self.robot_vx = 0
        self.robot_vy = 0
        self.prev_robot_x = 0
        self.prev_robot_y = 0
        self.V_max = 9  # Maximum voltage in volts
        self.t_final=10 # Simulation duration (in seconds)
        self.dt = 0.05 # Time step for the simulation

        # Initializing the ball 
        self.ball = Ball(self.HEIGHT // 2, self.WIDTH // 2, 0, 0,self.HEIGHT // 2, self.WIDTH // 2)

        self.running = True
        self.current_angle = 0
        self.current_speed = 0

        


    """Converting velocity from m/s to pixels/s."""
    def geschwindigkeit_umrechnen(self, geschwindigkeit_m_s):
        geschwindigkeit_mm_s = geschwindigkeit_m_s * 1000  # Conversion of meters to millimeters.
        geschwindigkeit_pixel_s = geschwindigkeit_mm_s * 0.2  # Application of the scaling factor 
        return geschwindigkeit_pixel_s

    """Converting velocity from pixels/s to m/s."""
    def pixelgeschwindigkeit_umrechnen(self, geschwindigkeit_pixel_s):
        geschwindigkeit_mm_s = geschwindigkeit_pixel_s / 0.2  
        geschwindigkeit_m_s = geschwindigkeit_mm_s / 1000  
        return geschwindigkeit_m_s
    
    def out_of_bounds(self,x,y,w,h):
        return(x<0 or x>w or y<0 or y>h)
    
        

    def robot_coordinates_update(self):
        self.prev_robot_x=self.robot_x
        self.prev_robot_y=self.robot_y

        self.robot_x += self.geschwindigkeit_umrechnen(self.current_speed) *self.dt * np.cos(np.radians(self.current_angle))
        self.robot_y -= self.geschwindigkeit_umrechnen(self.current_speed) *self.dt *np.sin(np.radians(self.current_angle))


        (self.x1,self.y1)=(self.robot_x + self.robot_height//2*np.cos(np.radians(self.current_angle)),self.robot_y - self.robot_height//2*np.sin(np.radians(self.current_angle)))
        (self.x2,self.y2)=(self.robot_x - self.robot_height//2*np.cos(np.radians(self.current_angle)),self.robot_y + self.robot_height//2*np.sin(np.radians(self.current_angle)))
        (self.x3,self.y3)=(self.robot_x + self.robot_width//2*np.sin(np.radians(self.current_angle)),self.robot_y + self.robot_width//2*np.cos(np.radians(self.current_angle)))
        (self.x4,self.y4)=(self.robot_x - self.robot_width//2*np.sin(np.radians(self.current_angle)),self.robot_y - self.robot_width//2*np.cos(np.radians(self.current_angle)))
        self.point_list=[(self.x1,self.y1),
                    (self.x2,self.y2),
                    (self.x3,self.y3),
                    (self.x4,self.y4),
                    (self.x1+ self.robot_width//2*np.sin(np.radians(self.current_angle)),self.y1+ self.robot_width//2*np.cos(np.radians(self.current_angle))),
                    (self.x1- self.robot_width//2*np.sin(np.radians(self.current_angle)),self.y1- self.robot_width//2*np.cos(np.radians(self.current_angle))),
                    (self.x2+ self.robot_width//2*np.sin(np.radians(self.current_angle)),self.y2+ self.robot_width//2*np.cos(np.radians(self.current_angle))),
                    (self.x2- self.robot_width//2*np.sin(np.radians(self.current_angle)),self.y2- self.robot_width//2*np.cos(np.radians(self.current_angle)))]

        for (x,y) in self.point_list:
            if self.out_of_bounds(x,y,self.HEIGHT,self.WIDTH):
                self.robot_x=self.prev_robot_x
                self.robot_y=self.prev_robot_y
    
    
    def reset(self):
        self.robot_x, self.robot_y = (self.HEIGHT // 2)-50, (self.WIDTH // 2)
        self.current_angle = 0
        self.current_speed = 0
        self.ball = Ball(self.HEIGHT // 2, self.WIDTH // 2, 0, 0,self.HEIGHT // 2, self.WIDTH // 2)
        self.running = True
        self.ball.right_team_score = 0
        self.ball.left_team_score = 0
        self.ball.right_goal_scored = False
        self.ball.left_goal_scored = False


    def _move(self, direction):
        if direction == Direction.RIGHT:
            self.current_angle -= 4
        elif direction == Direction.LEFT:
            self.current_angle += 4
        elif direction == Direction.STRAIGHT:
            self.current_speed += 0.2            

        if abs(self.current_speed)>=0.8:
            self.current_speed=math.copysign(0.8,self.current_speed)
        #print("phi="+str(self.current_angle))
        self.current_angle%=360

        self.robot_coordinates_update()
        #self.robot_wall_collision()

        self.ball.score_goal(910,0,217,175,5,self.ball_radius)

        if self.ball.right_goal_scored or self.ball.left_goal_scored:
            self.robot_x, self.robot_y = (self.HEIGHT // 2)-50, (self.WIDTH // 2)
            self.current_angle = 0
            self.ball.right_goal_scored = False
            self.ball.left_goal_scored = False

          



    
    def play_step(self):
        #self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT:
                        self.direction = Direction.RIGHT
                    elif event.key == pygame.K_UP:
                        self.direction = Direction.STRAIGHT
        #to be continued
        
        self._move(self.direction)
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(60)
        # 6. return game over and score
        return self.ball.left_team_score, self.ball.right_team_score
    

    def _update_ui(self):


        self.screen.fill(Gr.BLACK)
        # Drawing the game field
        Gr.draw_field()
        # Drawing the ball
        Gr.draw_ball(Gr.screen, self.ball, self.ball_radius, Gr.GREEN)     
        # Updating and drawing the robot
        Gr.update_robot(Gr.screen, self.robot_image, self.robot_x, self.robot_y, self.current_angle)



        # Updating the ball position
        self.ball.ball_bewegung(self.dt, self.ball_radius, self.HEIGHT, self.WIDTH,0)
        self.ball.ball_wand_kollision_x(self.HEIGHT, self.ball_radius )
        self.ball.ball_wand_kollision_y(self.WIDTH, self.ball_radius )

        # Collision detection and response
        self.robot_vx = self.geschwindigkeit_umrechnen(self.current_speed) * self.dt * np.cos(np.radians(self.current_angle))
        self.robot_vy = -self.geschwindigkeit_umrechnen(self.current_speed) *self.dt * np.sin(np.radians(self.current_angle))
        self.ball.kollision_detektion(self.dt, self.ball_radius, self.robot_x, self.robot_y, self.robot_width, self.robot_height, self.current_angle, 10*self.robot_vx, 10*self.robot_vy)
    


        # Calculating the ball's velocity 
        ball_speed_px_s = np.sqrt(self.ball.geschwindigkeit[0]**2 + self.ball.geschwindigkeit[1]**2)
        ball_speed_m_s = self.pixelgeschwindigkeit_umrechnen(ball_speed_px_s)

        # Display velocities of ball and robot on the screen

        ball_text = font.render(f"Velocity of the ball: {ball_speed_m_s:.2f} m/s", True, Gr.RED)
        robot_text = font.render(f"Velocity of the robot: {np.absolute(self.current_speed):.2f} m/s", True, Gr.RED)
        ball_position = (10, 30)
        speed_position = (10, 50)
        self.screen.blit(ball_text, ball_position)
        self.screen.blit(robot_text, speed_position)

        #display score 
        score_text = font.render(f"Right team score: {self.ball.right_team_score} Left team score: {self.ball.left_team_score}", True, Gr.RED)
        score_position = (10, 70)
        self.screen.blit(score_text, score_position)

        #display the ball coordinates
        ball_coordinates = font.render(f"Ball coordinates: ({round(self.ball.position[0])},{round(self.ball.position[1])})", True, Gr.RED)
        ball_coordinates_position = (10, 90)
        self.screen.blit(ball_coordinates, ball_coordinates_position)


        pygame.display.flip()  # Updating Displays
        pygame.time.delay(30)  # Pause to slow down the loop
        
    

        # Regulate the frames per second
        self.clock.tick(60)
    
    
    
    
    # integrate it into the update_ui function
    def goal_score_reset(self):
        if self.ball.right_goal_scored or self.ball.left_goal_scored:
            self.robot_x, self.robot_y = (self.HEIGHT // 2)-50, (self.WIDTH // 2)
            self.current_angle = 0
            self.ball.right_goal_scored = False
            self.ball.left_goal_scored = False




    # --------------- for display ------------------
    
    def robot_velocity(self):
        self.robot_vx = self.geschwindigkeit_umrechnen(self.current_speed) *self.dt * np.cos(np.radians(self.current_angle))
        self.robot_vy = -self.geschwindigkeit_umrechnen(self.current_speed) *self.dt * np.sin(np.radians(self.current_angle))    

    def ball_speed(self):
        self.ball_speed_px_s = np.sqrt(self.ball.geschwindigkeit[0]**2 + self.ball.geschwindigkeit[1]**2)
        self.ball_speed_m_s = self.pixelgeschwindigkeit_umrechnen(self.ball_speed_px_s)



if __name__ == '__main__':
    game = fussball_roboter()
    
    # game loop
    while True:
        game.play_step()
        
        
    pygame.quit()
        