import math
class Steuerung: # control
    def __init__(self, start_time, stop_time,V_max):
        self.start = start_time
        self.stop = stop_time
        self.last_u_recht = 0  # Initialize last_u with a default value
        self.last_u_left = 0  # Initialize last_u with a default value
        self.U= V_max

    def recht(self, time):
        #t=math.floor(time * 10) / 10
        t=round(time,2)
        if t == self.start:
            self.last_u_recht = 0
        elif t == self.stop:
            self.last_u_recht = self.U
        elif t == 5:
            self.last_u_recht = 0
        elif t == 6:
            self.last_u_recht = 0
        elif t == 7.9:
            self.last_u_recht = 0
        elif t == 10:
            self.last_u_recht = 0
        elif t == 15:
            self.last_u_recht = 0
        elif t == 16:
            self.last_u_recht = 0
        elif t == 17.9:
            self.last_u_recht = 0
        elif t == 20:
            self.last_u_recht = 0
        elif t == 25:
            self.last_u_recht = 0
        elif t == 26:
            self.last_u_recht = 0        
        elif t == 27.9:
            self.last_u_recht = 0
        elif t == 30:
            self.last_u_recht = 0
        elif t == 35:
            self.last_u_recht = 0

        return self.last_u_recht

    def link(self, time):

        t=round(time,2)
        if t == self.start:
            self.last_u_left =0
        elif t == self.stop:
            self.last_u_left = self.U*0.8
        elif t == 5:
            self.last_u_left = 0
        elif t == 6:
            self.last_u_left = 0
        elif t == 7.9:
            self.last_u_left = 0
        elif t == 10:
            self.last_u_left = 0
        elif t == 15:
            self.last_u_left = 0
        elif t == 16:
            self.last_u_left = 0
        elif t == 17.9:
            self.last_u_left = 0
        elif t == 20:
            self.last_u_left = 0
        elif t == 25:
            self.last_u_left = 0
        elif t == 26:
            self.last_u_left = 0         
        elif t == 27.9:
            self.last_u_left = 0
        elif t == 30:
            self.last_u_left = 0
        elif t == 35:
            self.last_u_left = 0
           
       

        

        return self.last_u_left

    
# class Steuerung:
#     def __init__(self, start_time, stop_time, V_max):
#         self.start = start_time
#         self.stop = stop_time
#         self.last_u_recht = 0  
#         self.last_u_left = 0  
#         self.U= V_max
#     def recht(self, time):
#         t = round(time, 2)
#         if self.start <= t < self.stop:
#             self.last_u_recht = self.U# The right wheel runs at maximum speed
#         return self.last_u_recht

#     def link(self, time):
#         t = round(time, 2)
#         if self.start <= t < self.stop:
#             self.last_u_left = 0.7 * self.U# The left wheel runs at 80% of the right wheel's speed
#         return self.last_u_left


