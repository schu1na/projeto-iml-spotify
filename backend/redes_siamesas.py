import torch.nn as nn
import torch.nn.functional as F

class SiameseNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, embedding_dim=32):
        super(SiameseNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),       # 11 → 128
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(hidden_size, hidden_size),      # 128 → 128
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(hidden_size, embedding_dim),    # 128 → 32
        )
        
    def forward_once(self, x):
        x = self.network(x)
        x = F.normalize(x, p=2, dim=1)
        return x
        
    def forward(self, input1, input2):
        output1 = self.forward_once(input1)
        output2 = self.forward_once(input2)
        return output1, output2