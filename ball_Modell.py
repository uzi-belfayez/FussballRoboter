import numpy as np
import math
import time

# The signum function returns the sign of a number.
def signum_block(x):
    return np.sign(x)

class Ball:
    
    def __init__(self, x, y , vx ,vy, initial_x, initial_y  ) -> None:
        # Initialize the properties of the ball.
        self.initial_x = initial_x
        self.initial_y = initial_y

        self.right_team_score = 0
        self.left_team_score = 0

        self.last_goal_time = 0  # Variable to store the time of the last goal
        self.goal_delay = 0.1  

        self.left_goal_scored = False
        self.right_goal_scored = False

        self.robot_ball_kollision = False
        
        self.Mb = 0.0012  # Ball Mass
        self.Mr = 0.6  # Robot Mass
        

        self.e_w= 0.5 # Energy loss coefficient during collision with the wall.
        self.k_rb = 0.95   # Energy loss coefficient during collision with the robot.
        self.reibung = 5 * 9.81  # Frictional force. 
        self.position = np.array([x, y], dtype=float)  # Initial position.
        self.geschwindigkeit = np.array([vx, vy], dtype=float)  # Initial velocity.
        
     
    def ball_bewegung(self, dt, ball_radius, HEIGHT, WIDTH ,winkel_b ): 
    	
        # Calculate and apply friction in the x- and y-directions.
        reibung_x = signum_block(round(self.geschwindigkeit[0],1)) * self.reibung * np.abs(np.cos(winkel_b))
        reibung_y = signum_block(round(self.geschwindigkeit[1],1)) * self.reibung * 1# np.abs(np.sin(winkel_b)) removed this cause the ball would never get friction on the Y axis

        # Update the position of the ball based on velocity and friction.
        self.geschwindigkeit[0] -= reibung_x * dt 
        self.geschwindigkeit[1] -= reibung_y * dt
        # putting dead zones
        if abs(self.geschwindigkeit[0])<4: 
            self.geschwindigkeit[0]=0
        if abs(self.geschwindigkeit[1])<4:
            self.geschwindigkeit[1]=0

        self.position[0] += self.geschwindigkeit[0]*dt
        self.position[1] += self.geschwindigkeit[1]*dt

       
        # Check and adjust the ball position if it touches the borders.
        if self.position[0] + ball_radius > HEIGHT:
            self.position[0] = HEIGHT - ball_radius
        if self.position[0] - ball_radius < 0:
            self.position[0] = ball_radius
        if self.position[1] + ball_radius >WIDTH:
            self.position[1] = WIDTH - ball_radius
        if self.position[1] -ball_radius < 0:
            self.position[1] = ball_radius  

    def ball_wand_kollision_x(self,HEIGHT,ball_radius):
        # Handling ball collision with the wall in the x-direction.
        if self.position[0] + ball_radius >= HEIGHT or self.position[0] - ball_radius <= 0:
            self.geschwindigkeit[0] = -self.geschwindigkeit[0] *self.e_w 
         
        return self.geschwindigkeit[0]

    def ball_wand_kollision_y(self,WIDTH,ball_radius):
        # Handling ball collision with the wall in the y-direction.
        if self.position[1] + ball_radius >= WIDTH or self.position[1] - ball_radius <= 0:        
           self.geschwindigkeit[1] = -self.geschwindigkeit[1] *self.e_w
         
        return self.geschwindigkeit[1]
          
    def kollision_detektion(self, dt , ball_radius, robot_x, robot_y, robot_width, robot_height, winkel, robot_vx, robot_vy):
        # Conversion of ball coordinates into the robot's coordinate system
        x1_ball = self.position[0] - robot_x
        y1_ball = self.position[1] - robot_y
        x2_ball = x1_ball * math.cos(math.radians(winkel))  - y1_ball * np.sin(math.radians(winkel))
        y2_ball = x1_ball * math.sin(math.radians(winkel)) + y1_ball * np.cos(math.radians(winkel))
        
        # Conversion of the velocity coordinates of the ball into the robot's coordinate system.
        vx_ball = self.geschwindigkeit[0] 
        vy_ball = self.geschwindigkeit[1] 
        vx1_ball = vx_ball * math.cos(math.radians(winkel)) - vy_ball * np.sin(math.radians(winkel))
        vy1_ball = vx_ball * math.sin(math.radians(winkel)) + vy_ball * np.cos(math.radians(winkel))
        
        # Conversion of the velocity coordinates of the robot into the robot's coordinate system.
        robot_vx1 = robot_vx * math.cos(math.radians(winkel)) - robot_vy * np.sin(math.radians(winkel))
        robot_vy1 = robot_vx * math.sin(math.radians(winkel)) + robot_vy * np.cos(math.radians(winkel))
        
        # Checking for collision between the ball and the robot.
        self.robot_ball_kollision = False
        if (-robot_height/2 <= x2_ball + ball_radius) and (robot_height/2 >= x2_ball - ball_radius) and (-robot_width/2 <= y2_ball) and (robot_width/2 >= y2_ball):
            self.robot_ball_kollision = True
        elif (-robot_height/2 <= x2_ball) and (robot_height/2 >= x2_ball) and (-robot_width/2 <= y2_ball + ball_radius) and (robot_width/2 >= y2_ball - ball_radius):
            self.robot_ball_kollision = True 
        elif np.sqrt((robot_height/2 - x2_ball)**2 +  (robot_width/2- y2_ball)**2) <= ball_radius or \
             np.sqrt((-robot_height/2 - x2_ball)**2 +  (robot_width/2- y2_ball)**2) <= ball_radius or \
             np.sqrt((robot_height/2 - x2_ball)**2 +  (-robot_width/2- y2_ball)**2) <= ball_radius or \
             np.sqrt((-robot_height/2 - x2_ball)**2 +  (-robot_width/2- y2_ball)**2) <= ball_radius :       
             self.robot_ball_kollision = True
                          
        # Handling the collision of the ball with the left side of the robot.
        if self.robot_ball_kollision:
            if -robot_height/2 >= x2_ball and -robot_width/2 <= y2_ball and robot_width/2 >= y2_ball:
                vx1_ball = (vx1_ball * self.Mb + robot_vx1 * self.Mr) / (self.Mb + self.Mr) - ( (vx1_ball-robot_vx1 )*self.k_rb * self.Mr ) / (self.Mb + self.Mr)
                robot_vx1 =(vx1_ball * self.Mb + robot_vx1 * self.Mr) / (self.Mb + self.Mr) -  ( (robot_vx1- vx1_ball)*self.k_rb * self.Mb ) / (self.Mb + self.Mr)
                
                x2_ball = -robot_height/2 - ball_radius

            # Handling the collision of the ball with the right side of the robot.
            if robot_height/2 <= x2_ball and -robot_width/2 <= y2_ball and robot_width/2 >= y2_ball:

                vx1_ball = (vx1_ball * self.Mb + robot_vx1 * self.Mr) / (self.Mb + self.Mr) - ( (vx1_ball-robot_vx1 )*self.k_rb * self.Mr ) / (self.Mb + self.Mr)
                robot_vx1 =(vx1_ball * self.Mb + robot_vx1 * self.Mr) / (self.Mb + self.Mr) -  ( (robot_vx1- vx1_ball)*self.k_rb * self.Mb ) / (self.Mb + self.Mr)
               
                x2_ball = robot_height/2 +  ball_radius

            # Handling the collision of the ball with the top side of the robot.
            if -robot_width/2 >= y2_ball and -robot_height/2 <= x2_ball and robot_height/2 >= x2_ball:

                vy1_ball = (vy1_ball * self.Mb + robot_vy1 * self.Mr) / (self.Mb + self.Mr) - ( (vy1_ball-robot_vx1 )*self.k_rb * self.Mr ) / (self.Mb + self.Mr)
                robot_vy1 = (vy1_ball * self.Mb + robot_vy1 * self.Mr) / (self.Mb + self.Mr) -  ( (robot_vy1- vy1_ball)*self.k_rb * self.Mb ) / (self.Mb + self.Mr)
                
                y2_ball = -robot_width/2 - ball_radius

            # Handling the collision of the ball with the bottom side of the robot.
            if robot_width/2 <= y2_ball and -robot_height/2 <= x2_ball and robot_height/2 >= x2_ball:
                
                vy1_ball =   (vy1_ball * self.Mb+ robot_vy1 * self.Mr) / (self.Mb + self.Mr) - ( (vy1_ball-robot_vx1 )*self.k_rb * self.Mr ) / (self.Mb + self.Mr)
                robot_vy1 = (vy1_ball * self.Mb + robot_vy1 * self.Mr) / (self.Mb + self.Mr) -  ( (robot_vy1- vy1_ball)*self.k_rb * self.Mb ) / (self.Mb + self.Mr)
              
                y2_ball = robot_width/2 + ball_radius

               # Collision between the ball and the upper left corner of the robot.
            if -robot_height/2 >= x2_ball and -robot_width/2 >= y2_ball:
                if abs(-robot_width/2-y2_ball) >= abs(-robot_height/2-x2_ball):
                    vy1_ball = -vy1_ball*self.k_rb
                else:
                    vx1_ball= -vx1_ball*self.k_rb
           
            # Collision between the ball and the upper right corner of the robot.
            if robot_height/2 <= x2_ball and -robot_width/2 >= y2_ball :
                if abs(-robot_width/2-y2_ball) > abs(robot_height/2-x2_ball):
                    vy1_ball = -vy1_ball*self.k_rb
                else:
                    vx1_ball= -vx1_ball*self.k_rb
                
            # Collision between the ball and the lower left corner of the robot.
            if -robot_height/2 >= x2_ball and robot_width/2 <= y2_ball :
                # Bestimmung nach Eckkollision
                if abs(robot_width/2-y2_ball) >= abs(-robot_height/2-x2_ball):
                    vy1_ball = -vy1_ball*self.k_rb
                else:
                    vx1_ball= -vx1_ball*self.k_rb
               
            # Collision between the ball and the lower right corner of the robot.        
            if robot_height/2 <= x2_ball and robot_width/2 <= y2_ball :
                # Bestimmung nach Eckkollision
                if abs(robot_width/2-y2_ball) >= abs(robot_height/2-x2_ball):
                    vy1_ball = -vy1_ball*self.k_rb
                else:
                    vx1_ball= -vx1_ball*self.k_rb

            # Conversion of the ball coordinates from the robot's coordinate system back into the world coordinate system.
            winkel = - winkel   
            vx2_ball = vx1_ball * math.cos(math.radians(winkel)) - vy1_ball * np.sin(math.radians(winkel))
            vy2_ball = vx1_ball * math.sin(math.radians(winkel)) + vy1_ball * np.cos(math.radians(winkel))

            self.geschwindigkeit[0] = vx2_ball
            self.geschwindigkeit[1] = vy2_ball
            
            x3_ball = x2_ball * math.cos(math.radians(winkel)) - y2_ball * np.sin(math.radians(winkel)) + robot_x
            y3_ball = x2_ball * math.sin(math.radians(winkel)) + y2_ball * np.cos(math.radians(winkel)) + robot_y

            self.position[0] = x3_ball
            self.position[1] = y3_ball    

    def score_goal(self, right_goal_x, left_goal_x, goal_y, height, width, ball_radius):

        if time.time() - self.last_goal_time > self.goal_delay:
            if (self.position[0]-ball_radius < (left_goal_x + width)) & (self.position[1]+ball_radius > goal_y) & (self.position[1]+ball_radius < (goal_y+height)):
                print("Goal scored by right team")
                self.right_team_score = self.right_team_score + 1
                self.position[0] = self.initial_x
                self.position[1] = self.initial_y
                self.geschwindigkeit[0] = 0
                self.geschwindigkeit[1] = 0
                self.last_goal_time = time.time()
                self.right_goal_scored = True
            elif (self.position[0]+ball_radius > right_goal_x) & (self.position[1]+ball_radius > goal_y) & (self.position[1]+ball_radius < (goal_y + height)):
                print("Goal scored by left team")
                print("HERE!")
                self.left_team_score = self.left_team_score + 1
                self.position[0] = self.initial_x
                self.position[1] = self.initial_y
                self.geschwindigkeit[0] = 0
                self.geschwindigkeit[1] = 0
                self.last_goal_time = time.time()
                self.left_goal_scored = True
        #return right_team_score, left_team_score


    def reset(self):
        # Reset the ball to its initial position.
        self.position[0] = self.initial_x
        self.position[1] = self.initial_y
        self.geschwindigkeit[0] = 0
        self.geschwindigkeit[1] = 0
        self.right_team_score = 0
        self.left_team_score = 0
        self.last_goal_time = 0



        


""" Within the ball_movement function, the simulation begins by calculating the friction of the ball in the x and y directions. The signum_block function [3] is used to determine the sign of the velocity components. If the velocity in the x direction (vx) is positive, it returns 1.0. If vx is negative, it returns -1.0. If vx is zero, it returns 0.0, and the same for vy. This ensures that the velocity and friction have the same sign.
        After the calculation, the ball's velocity is adjusted. The friction is multiplied by the time increment (dt), and this value is subtracted from the ball's old velocity. This means the ball slows down due to friction.
        Next, the ball's position is updated based on this adjusted velocity.
        Then, boundary conditions are checked. If the ball touches the boundaries of the football field, its position is corrected to ensure it remains within these boundaries.
        It was decided to correct the position because otherwise, simulation display issues could arise. """
       
