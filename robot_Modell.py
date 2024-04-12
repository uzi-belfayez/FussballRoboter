import numpy as np
import math
from scipy.integrate import quad


class Modell:
    # Simulation parameters of the electric motors.
    R = 4.96  # Resistance. (in Ohm)
    thetam = 0.0024  # Moment of inertia. (in kg*m^2)
    b = 0.001  # Friction coefficient. (in N*m*s)
    Km = 0.235  # Torque constant. (in N*m/A)
    Ku = 0.506  # Back-EMF constant. (in V*s/rad)
   
    dt = 0.05 # Time step (in seconds).
    t_final = 10 # Simulation duration (in seconds).

    # Robot dynamics.
    M = 0.6  # Robot Mass
    L = 0.063  # Distance between the wheels in meters.
    D = 0.06 # Distance from the support ball to the axis of rotation.
    r = 0.0275  # Wheel radius.
    mr = 0.02  # Mass moment of inertia of the wheel and the motor.
    
    thetar = (0.5 * mr * r**2) + thetam  # Mass moment of inertia.
    ThetaA = 0.0011  # Mass moment of inertia of the robot.
    # c = 0.033 
    # Friction.
    f_r = 2.35
    mu = 0.15
    RE = f_r * mu
    # Initial values.
    I_L = 0.0  # Current (in Amperes).
    I_R = 0.0  # Current (in Amperes).
    v = 0.0  # Robot velocity.
    w = 0.0  # Robot angular velocity.
    wl = 0.0
    wr = 0.0
    s_x = 0.0
    s_y = 0.0
    winkel=0.0
    """
    Simulates the dynamics of the electric motor and robot.

    Args:
        motor_recht (function): Function representing the right motor's input voltage over time.
        motor_link (function): Function representing the left motor's input voltage over time.

    Returns:
        tuple: Returns arrays containing time, speed, angular velocities of left and right wheels,
               linear velocities of left and right wheels, x and y positions.
      """
   
    def simulate(self, motor_recht,motor_link):
    
        # Arrays to store simulation results.
        time = np.arange(0.0, self.t_final, self.dt)  # From zero to end with sampling interval dt.
        speed = np.zeros_like(time)
        w_left = np.zeros_like(time)
        w_right = np.zeros_like(time)
        v_left = np.zeros_like(time)
        v_right = np.zeros_like(time)
        x = np.zeros_like(time)
        y = np.zeros_like(time)
        winkel = np.zeros_like(time)
        accel = np.zeros_like(time)
        

        def signum_block(x):
            return np.sign(x)
       
        # Simulation loop
        for i, t in enumerate(time):
            # Direct current (DC) motor
           

# Define the desired speeds for the PID controller
             
            U_R=motor_recht(t)
            U_L=motor_link(t)
            
            I_L = (U_L - self.Ku * self.wl) / self.R
            I_R = (U_R - self.Ku * self.wr) / self.R
            ML = self.Km * I_L
            MR = self.Km * I_R
            # Dynamic
            
            reibung_v = signum_block(round(self.v,1)) * self.RE
            
            reibung_w=signum_block(round(self.w,1))*self.RE
            
           
    
            accel_r = ((MR + ML) * self.r) / (self.M * self.r * self.r + 2 * self.mr * self.r * self.r + 2 * self.thetar) - reibung_v
            omega_punkt_r = (MR - ML) * self.r * self.L / (self.ThetaA * self.r * self.r + 2 * self.L * self.L * self.r * self.r * self.mr + 2 * self.thetar * self.L * self.L)-reibung_w
            
            
            
            
            self.v += accel_r * self.dt  
            self.w = omega_punkt_r * self.dt
            self.winkel +=self.w *self.dt
            
            # Kinematics
            self.wl = (self.v + self.w * self.L) / self.r
            self.wr = (self.v - self.w * self.L) / self.r
            self.vl=self.wl *self.r
            self.vr=self.wr *self.r
            # Global coordinates
            v_x = np.cos(self.winkel)
            v_y = np.sin(self.winkel)
            self.s_x += v_x * self.dt
            self.s_y += v_y * self.dt
            # Saving the values
            speed[i] = self.v
            
            w_left[i] = self.wl
            w_right[i] = self.wr
            v_left[i] = self.vl
            v_right[i] = self.vr
            x[i] = self.s_x
            y[i] = self.s_y
            winkel[i]=(self.winkel)*180/math.pi
            accel[i]=accel_r
            
            
           
            
        return time, speed, w_left, w_right,v_left,v_right, x, y,winkel,accel
