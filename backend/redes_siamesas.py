import torch.nn as nn
import torch.nn.functional as F

class MapeadorSiames(nn.Module):
    def __init__(self, input_size, hidden_size, embedding_dim=32):
        super(MapeadorSiames, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, embedding_dim)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x