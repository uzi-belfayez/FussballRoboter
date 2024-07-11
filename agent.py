from collections import deque
import torch
import random
import numpy as np

from game_fussball_roboter_ai import fussball_roboter
from model import Linear_QNet, Q_Trainer
from helper import plot,plot_rewards
import os
possible_actions = [[1, 0, 0],#rotate left
                    [0, 1, 0],#forward
                    [0, 0, 1],#rotate right
                    [0, 0 ,0],#do nothing
                    [0,-1 ,0] #reduce speed until stop (brake)
                    ]
# Initialize Q(s,a) arbitrarily
# Repeat (for each generation):
# 	Initialize state s
# 	While (s is not a terminal state):		
# 		Choose a from s using policy derived from Q
# 		Take action a, observe r, s'
# 		Q(s,a) += alpha * (r + gamma * max,Q(s') - Q(s,a))
# 		s = s'

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR =0.01

# Save the current learning rate to a file
def save_learning_rate(learning_rate, filename='./model/learning_rate.txt'):
    with open(filename, 'w') as f:
        f.write(str(learning_rate))

# Load the learning rate from a file
def load_learning_rate(filename='./model/learning_rate.txt'):
    try:
        with open(filename, 'r') as f:
            learning_rate = float(f.read())
    except FileNotFoundError:
        learning_rate = None
    return learning_rate

class Agent:
    def __init__(self,file_name='model.pth',n_inputs=10,n_hidden=128,n_outputs=5,learning_rate=0.1,device='cpu') -> None:
        self.n_games = 0

        #randomness
        self.epsilon = 0.5
        self.epsilon_decay = 0.995 
        #learning rate
        self.alpha=learning_rate
        self.alpha_decay = 0.95

        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.n_random_actions=0
        self.n_best_possible_actions=0
        
        # Check if the model file exists
        model_folder_path = "./model"
        full_path = os.path.join(model_folder_path,file_name)
        if os.path.exists(full_path):
            # Load model
            self.model = Linear_QNet.load(full_path,n_inputs, n_hidden, n_outputs, device)
            print("Model loaded successfully!")
        else:
            print(f"Model file '{file_name}' not found. Training new model...")
            # Train new model
            self.model = Linear_QNet(n_inputs, n_hidden, n_outputs, device)
        self.trainer = Q_Trainer(self.model,self.alpha,self.gamma)

    def get_state(self, game:fussball_roboter):
        return np.array(game.vision())
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory)>BATCH_SIZE:
            sample=random.sample(self.memory,BATCH_SIZE)
        else:
            sample=self.memory
        states,actions,rewards,next_states,dones=zip(*sample)
        self.trainer.train_step(states,actions,rewards,next_states,dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    def get_action(self,state):
        
        # Epsilon-greedy policy
        if random.uniform(0, 1) < self.epsilon:
            # Explore: Choose a random action
            action = random.choice(possible_actions)
            self.n_random_actions+=1

        else:
            #Exploit: Choose the best possible action
            state0 = torch.tensor(state,dtype=torch.float).to(self.model.device)
            prediction = self.model(state0)
            action=possible_actions[torch.argmax(prediction).item()]
            self.n_best_possible_actions+=1

        


        # Decay epsilon over time
        # self.epsilon *= self.epsilon_decay

        return action
                
def format(vision:list):
    print("ROBOT")
    print("Coordinates:",(vision[0],vision[1]))
    print("Current angle:",vision[2])
    print("Current speed:",vision[3])
    print("\nBALL")
    print("Ball coordinates:",(vision[4],vision[5]))
    print("Ball distance:",vision[6])
    print("Ball angle:",vision[7])
    print("\nGOAL")
    print("Goal distance:",vision[8])
    print("Goal angle:",vision[9])

def train():
    plot_scores=[]
    plot_mean_scores=[]
    plot_positive_rewards=[]
    plot_negative_rewards=[]
    total_score=0
        # Check if CUDA is available
    if torch.cuda.is_available():
        device = torch.device("cuda")          # a CUDA device object
        print("CUDA is available. Using GPU.")
    else:
        device = torch.device("cpu")           # a CPU device object
        print("CUDA is not available. Using CPU.")
    # Now you can move tensors and models to the selected device
    # tensor = torch.randn(3, 3).to(device)

    lr=load_learning_rate()
    if lr is not None:
        print("Loaded learning rate!")
    else:
        lr=LR
        print(f"File not found, proceeding with default LR of {lr}")
    


    agent=Agent(device=device,learning_rate=lr)
    for name, param in agent.model.named_parameters():
        print(f"Parameter {name} is on device: {param.device}")
    record=0
    game=fussball_roboter()
    accumulated_negative_reward=0
    accumulated_positive_reward=0
    
    while True:
        #get old state
        state=agent.get_state(game)
        # get action
        action=agent.get_action(state)
        # perform action
        reward,done,score=game.play_step(action)
        # get new state
        if reward>0:
            # print(reward)
            accumulated_positive_reward+=reward
        elif reward<0:
            # print(reward)
            accumulated_negative_reward+=reward
        next_state=agent.get_state(game)
        #train short memory
        agent.train_short_memory(state,action,reward,next_state,done)
        # remember
        agent.remember(state, action, reward, next_state, done)
        # last_vision=game.vision()
        if done:
            game.reset()
            agent.n_games+=1

            agent.epsilon*=agent.epsilon_decay
            agent.train_long_memory()
            if agent.n_games%10==0:
                agent.model.save()
                print("Model saved!")
            if score>record and score>0:
                record=score
                agent.model.save()
                print("Model saved!")
                agent.alpha*=agent.alpha_decay
                save_learning_rate(agent.alpha)
                print("Learning rate saved!")
            print('Game', agent.n_games, 'Score', score, 'Record:', record,'Epsilon:',agent.epsilon,'Alpha:',agent.alpha)
            
            print('Total actions taken: ',agent.n_random_actions+agent.n_best_possible_actions)
            print('Random actions taken: ',agent.n_random_actions)
            print('Best actions taken: ',agent.n_best_possible_actions)
            
            agent.n_best_possible_actions=0
            agent.n_random_actions=0
            

            plot_scores.append(score)
            total_score+=score
            mean_score=total_score/agent.n_games
            plot_mean_scores.append(mean_score)
            plot_positive_rewards+=[accumulated_positive_reward]
            plot_negative_rewards+=[accumulated_negative_reward]
            plot(plot_scores,plot_mean_scores)
            plot_rewards(plot_positive_rewards,plot_negative_rewards)
            # format(last_vision)
            # input("Press Enter to continue...")





    
            
if __name__ == '__main__':
    
    train()
    # game = SnakeGame()
    
    # # game loop
    # while True:
    