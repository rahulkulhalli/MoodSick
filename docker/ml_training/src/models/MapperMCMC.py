import torch.nn as nn
import torch.nn.functional as F


class MapperMCMC(nn.Module):
    def __init__(self):
        super(MapperMCMC, self).__init__()
        self.linear1 = nn.Linear(1024, 1024)
        self.linear2 = nn.Linear(1024, 256)
        self.linear3 = nn.Linear(256, 12)

    def forward(self, x):
        x = F.dropout(F.relu(self.linear1(x)), p=0.5)
        x = F.dropout(F.relu(self.linear2(x)), p=0.5)
        return self.linear3(x)

    @staticmethod
    def enable_dropout_in_eval(model: nn.Module):
        for m in model.modules():
            if m.__class__.__name__.lower().startswith('dropout'):
                m.train()
