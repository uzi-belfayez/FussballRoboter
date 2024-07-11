import pygame
import math
import numpy as np
import graphischedarsetllung as Gr
from spannung_steuerun import Steuerung
from ball_Modell import Ball
import matplotlib.pyplot as plt
from enum import Enum
from random import randint

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

        self.key_state =   {pygame.K_UP:    0,
                            pygame.K_DOWN:  0,
                            pygame.K_RIGHT: 0,
                            pygame.K_LEFT:  0}
        self.keys = {pygame.K_UP:"K_UP",
                pygame.K_DOWN:"K_DOWN",
                pygame.K_RIGHT:"K_RIGHT",
                pygame.K_LEFT:"K_LEFT"}
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
                #goal parameters
        self.home_goal_x=910
        self.away_goal_x=0
        self.goal_y=217
        self.height=175
        self.width=5
        random_ball_xy=(randint(self.HEIGHT // 2+100, self.HEIGHT -100),randint(50, self.WIDTH-50))
        print(self.HEIGHT // 2+100)
        # Initializing the ball 
        self.ball = Ball(*random_ball_xy, 0,0,self.HEIGHT // 2, self.WIDTH // 2)

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
    def euclidean_distance(self,x, y):
        return math.sqrt((x - self.robot_x)**2 + (y - self.robot_y)**2)
        
    def vision(self):
        ball_position=[self.ball.position[0],self.ball.position[1]]
        ball_distance=self.euclidean_distance(*ball_position)
        goal_position=(self.home_goal_x,self.goal_y+176/2)
        goal_distance=self.euclidean_distance(*goal_position)
       
        # vision={
        #     "position":(self.robot_x,self.robot_y),#Coordinates
        #     "angle":self.current_angle,#Current angle
        #     "speed":self.current_speed,#Speed
        #     "ball position":ball_position,#Ball Coordinates
        #     "ball distance":ball_distance,#distance to ball
        #     "ball angle":math.degrees(math.copysign(1,self.robot_y-ball_position[1])*
        #     math.acos((-self.robot_x+ball_position[0])/ball_distance))%360,#angle to ball
        #     "goal distance":goal_distance,#distance to goal
        #     "goal angle":math.degrees(math.asin((self.robot_y-goal_position[1])/goal_distance))%360#angle to goal
        # }


        vision=[
            self.robot_x,self.robot_y,#Coordinates
            self.current_angle,#Current angle
            self.current_speed,#Speed
            self.ball.position[0],self.ball.position[1],#Ball Coordinates
            ball_distance,#distance to ball
            math.degrees(math.copysign(1,self.robot_y-ball_position[1])*math.acos((-self.robot_x+ball_position[0])/ball_distance))%360,#angle to ball
            goal_distance,#distance to goal
            math.degrees(math.asin((self.robot_y-goal_position[1])/goal_distance))%360#angle to goal
        ]
        return np.array(vision,dtype=float)    
        
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
                print("here")
                self.robot_x=self.prev_robot_x
                self.robot_y=self.prev_robot_y
                self.current_angle=self.previous_angle
    
    
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


    def _move(self):
          
        self.current_speed+= 0.2*(self.key_state[pygame.K_UP]-self.key_state[pygame.K_DOWN])
        self.previous_angle=self.current_angle
        self.current_angle+= 4*(self.key_state[pygame.K_LEFT]-self.key_state[pygame.K_RIGHT])
        
        if self.current_speed>=0.8:
            self.current_speed=0.8
        if self.current_speed<0 or self.key_state[pygame.K_UP]+self.key_state[pygame.K_DOWN]==0:
            self.current_speed=0
            
        
            
        #print("phi="+str(self.current_angle))
        self.current_angle%=360

        self.robot_coordinates_update()
        #self.robot_wall_collision()

        # self.ball.score_goal(self.home_goal_x, self.away_goal_x, self.goal_y, self.height, self.width,self.ball_radius)
        
        # if self.ball.right_goal_scored or self.ball.left_goal_scored:
        #     self.robot_x, self.robot_y = (self.HEIGHT // 2)-50, (self.WIDTH // 2)
        #     self.current_angle = 0
        #     self.ball.right_goal_scored = False
        #     self.ball.left_goal_scored = False

          



    
    def play_step(self):
        #self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                self.key_state[event.key] = 1  # Set the key to pressed
            elif event.type == pygame.KEYUP:
                self.key_state[event.key] = 0  # Set the key to released
        #to be continued
        
        self._move()
        
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

        self.ball.kollision_detektion(self.dt, self.ball_radius, self.robot_x, self.robot_y, self.robot_width, self.robot_height, self.current_angle, 20*self.robot_vx, 20*self.robot_vy)
    


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
      

        # Regulate the frames per second

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
     
        # print("goal angle:",dict['goal angle'])
        
        
        
    pygame.quit()
        