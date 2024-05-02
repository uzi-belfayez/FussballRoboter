import torch
import random
import numpy as np
from game_fussball_roboter_ai import fussball_roboter, Direction
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game_fussball_roboter):

        dir_l = game_fussball_roboter.direction == Direction.LEFT
        dir_r = game_fussball_roboter.direction == Direction.RIGHT
        dir_u = game_fussball_roboter.direction == Direction.UP
        dir_d = game_fussball_roboter.direction == Direction.DOWN



        state = [

        #goal location
        game_fussball_roboter.robot_y < 217, # goal is on the right
        game_fussball_roboter.robot_y > 217,  # goal is on the left       
        
        # Move direction
        dir_l,
        dir_r,
        dir_u,
        dir_d,

        #ball location 
        game_fussball_roboter.ball.y > game_fussball_roboter.robot_y, # ball is on the right
        game_fussball_roboter.ball.y < game_fussball_roboter.robot_y,# ball is on the left
        game_fussball_roboter.ball.x > game_fussball_roboter.robot_x, # ball is in front of the robot
        game_fussball_roboter.ball.x < game_fussball_roboter.robot_x # ball is behind the robot

        ]
