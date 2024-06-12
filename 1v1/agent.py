import torch
import random
import numpy as np
from game_1v1_ai import fussball_roboter, Direction
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot
from ball_Modell import Ball

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
        self.model1 = Linear_QNet(11, 256, 3)
        self.trainer1 = QTrainer(self.model1, lr=LR, gamma=self.gamma)

    def get_state(self, fussball_roboter):

        dir_l = fussball_roboter.direction == Direction.LEFT
        dir_r = fussball_roboter.direction == Direction.RIGHT
        dir_u = fussball_roboter.direction == Direction.STRAIGHT


        state = [
        #goal location
        fussball_roboter.robot_y < 217, # goal is on the right
        fussball_roboter.robot_y > 217,  # goal is on the left       
        # Move direction
        dir_l,
        dir_r,
        dir_u,
        #ball location 
        fussball_roboter.ball.position[1] > fussball_roboter.robot_y, # ball is on the right
        fussball_roboter.ball.position[1] < fussball_roboter.robot_y, # ball is on the left
        fussball_roboter.ball.position[0] > fussball_roboter.robot_x, # ball is in front of the robot
        fussball_roboter.ball.position[0] < fussball_roboter.robot_x, # ball is behind the robot
        fussball_roboter.robot_x1,
        fussball_roboter.robot_y1

        ]
        return np.array(state, dtype=int)
    
    def get_state1(self, fussball_roboter):

        dir_l1 = fussball_roboter.direction1 == Direction.LEFT
        dir_r1 = fussball_roboter.direction1 == Direction.RIGHT
        dir_u1 = fussball_roboter.direction1 == Direction.STRAIGHT


        state1 = [
        #goal location
        fussball_roboter.robot_y1 < 217, # goal is on the right
        fussball_roboter.robot_y1 > 217,  # goal is on the left       
        # Move direction
        dir_l1,
        dir_r1,
        dir_u1,
        #ball location 
        fussball_roboter.ball.position[1] > fussball_roboter.robot_y1, # ball is on the right
        fussball_roboter.ball.position[1] < fussball_roboter.robot_y1, # ball is on the left
        fussball_roboter.ball.position[0] > fussball_roboter.robot_x1, # ball is in front of the robot
        fussball_roboter.ball.position[0] < fussball_roboter.robot_x1, # ball is behind the robot
        fussball_roboter.robot_x,
        fussball_roboter.robot_y

        ]
        return np.array(state1, dtype=int)
    

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached


    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards,next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_long_memory1(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample1 = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample1 = self.memory

        states1, actions1, rewards1,next_states1, dones1 = zip(*mini_sample1)
        self.trainer1.train_step(states1, actions1, rewards1, next_states1, dones1)


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)


    def get_action(self, state):
        #random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move
    
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    plot_scores1 = []
    plot_mean_scores1 = []
    total_score1 = 0
    record1 = 0
    agent = Agent()
    game = fussball_roboter()

    while True:
        # get old state
        state_old = agent.get_state(game)
        state_old1 = agent.get_state1(game)

        # get move
        final_move = agent.get_action(state_old)
        final_move1 = agent.get_action(state_old1)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        reward1, done1, score1 = game.play_step1(final_move1)
        state_new1 = agent.get_state1(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        agent.train_short_memory(state_old1, final_move1, reward1, state_new1, done1)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        agent.remember(state_old1, final_move1, reward1, state_new1, done1)

        if done or done1:
            # train long memory
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            agent.train_long_memory1()

            if score > record :
                record = score
                agent.model.save()
            if score1 > record1 :
                record1 = score1
                agent.model1.save1()

            print('Game', agent.n_games, 'Score', score,'-',score1, 'Record:', record,'Record1:', record1)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

            plot_scores1.append(score1)
            total_score1 += score1
            mean_score1 = total_score1 / agent.n_games
            plot_mean_scores1.append(mean_score1)
            plot(plot_scores1, plot_mean_scores1)


if __name__ == '__main__':
    train()