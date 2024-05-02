import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


class Linear_QNet(nn.Module):
    def __init__(self, n_inputs=11,n_hidden=256,n_output=3,device='cpu') -> None:
        super().__init__()
        self.device=device
        self.to(device)
        self.linear1=nn.Linear(n_inputs,n_hidden).to(device)
        self.linear2=nn.Linear(n_hidden,n_output).to(device)
    def forward(self,x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    def save(self, file_name="model.pth"):
        model_folder_path = "./model"
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        full_path = os.path.join(model_folder_path,file_name)
        torch.save(self.state_dict(),full_path)
    
    @staticmethod
    def load(file_path, device='cpu'):
        if os.path.exists(file_path):
            model = Linear_QNet(device=device)  # Create an instance of the model
            model.load_state_dict(torch.load(file_path, map_location=device))
            model.to(device)  # Move model to the specified device
            return model
        else:
            raise FileNotFoundError(f"Model file '{file_path}' not found.")

class Q_Trainer:
    def __init__(self,model:Linear_QNet,lr,gamma) -> None:
        self.model=model
        self.lr=lr
        self.gamma=gamma
        self.optimizer = optim.Adam(model.parameters(),lr=self.lr)
        self.criterion = nn.MSELoss()
    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state,dtype=torch.float).to(self.model.device)
        action = torch.tensor(action,dtype=torch.long).to(self.model.device)
        reward = torch.tensor(reward,dtype=torch.float).to(self.model.device)
        next_state = torch.tensor(next_state,dtype=torch.float).to(self.model.device)
        #{n,x}

        if len(state.shape)==1:
            #{1,x}
        
            state = torch.unsqueeze(state,0)
            action = torch.unsqueeze(action,0)
            reward = torch.unsqueeze(reward,0)
            next_state = torch.unsqueeze(next_state,0)
            done=(done,)
        #1:predicted Q values with current state
        pred=self.model(state)
        target=pred.clone()
        for index in range(len(done)):
            Q_new = reward[index]
            if not done[index]:
                Q_new = reward[index] + self.gamma * torch.max(self.model(next_state[index]))
            
            target[index][torch.argmax(action[index]).item()] = Q_new
                
        #2: Q_new=r + y * max(next_predicted Q value)
        self.optimizer.zero_grad()
        loss = self.criterion(target,pred)
        loss.backward()
        self.optimizer.step()
    
        