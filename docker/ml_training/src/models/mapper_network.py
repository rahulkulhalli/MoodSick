import torch
import torch.nn as nn
import torch.nn.functional as F
import pyro
from pyro.nn import PyroModule, PyroSample
import pyro.distributions as dist

class MappingNetwork(PyroModule):
    def __init__(self, fan_in: int = 1024, fan_out: int = 12, device=None):
        super().__init__()

        self.f_in = fan_in
        self.f_out = fan_out

        self.linear1 = PyroModule[nn.Linear](fan_in, fan_in)
        self.linear1.weight = PyroSample(
            dist.Normal(0., torch.tensor(1.0, device=device)).expand([fan_in, fan_in]).to_event(2)
        )
        self.linear1.bias = PyroSample(
            dist.Normal(0., torch.tensor(1.0, device=device)).expand([fan_in]).to_event(1)
        )

        self.linear2 = PyroModule[nn.Linear](fan_in, 256)
        self.linear2.weight = PyroSample(
            dist.Normal(0., torch.tensor(1.0, device=device)).expand([256, fan_in]).to_event(2)
        )
        self.linear2.bias = PyroSample(
            dist.Normal(0., torch.tensor(1.0, device=device)).expand([256]).to_event(1)
        )

        self.linear3 = PyroModule[nn.Linear](256, fan_out)
        self.linear3.weight = PyroSample(
            dist.Normal(0., torch.tensor(1.0, device=device)).expand([fan_out, 256]).to_event(2)
        )
        self.linear3.bias = PyroSample(
            dist.Normal(0., torch.tensor(1.0, device=device)).expand([fan_out]).to_event(1)
        )

    def forward(self, x, y=None):
        mean = F.relu(self.linear1(x))
        mean = F.relu(self.linear2(mean))
        mean = self.linear3(mean)

        # Draw sigma from a uniform distribution
        sigma = pyro.sample("sigma", dist.Uniform(0., 10.).expand([self.f_out]).to_event(1))

        with pyro.plate("data", x.shape[0]):
            obs = pyro.sample("obs", dist.Normal(mean, sigma).to_event(1), obs=y)

        return mean
