import torch.nn as nn


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.act = nn.ReLU()
        self.bn = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)

    def forward(self, x):
        residual = x
        x = self.act(self.bn(self.conv2(self.act(self.bn(self.conv1(x))))))
        return x + residual


class MapperMCMC(nn.Module):
    def __init__(self):
        super(MapperMCMC, self).__init__()
        self.act = nn.ReLU()
        self.dpt = nn.Dropout(p=0.5)

        self.conv1 = nn.Conv1d(1024, 512, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn1 = nn.BatchNorm1d(512)
        self.res1 = ResidualBlock(512, 512)
        self.res12 = ResidualBlock(512, 512)

        self.conv2 = nn.Conv1d(512, 256, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn2 = nn.BatchNorm1d(256)
        self.res2 = ResidualBlock(256, 256)
        self.res22 = ResidualBlock(256, 256)

        self.conv3 = nn.Conv1d(256, 128, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn3 = nn.BatchNorm1d(128)
        self.res3 = ResidualBlock(128, 128)
        self.res32 = ResidualBlock(128, 128)

        self.conv4 = nn.Conv1d(128, 64, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn4 = nn.BatchNorm1d(64)
        self.res4 = ResidualBlock(64, 64)
        self.res42 = ResidualBlock(64, 64)

        self.conv5 = nn.Conv1d(64, 32, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn5 = nn.BatchNorm1d(32)
        self.res5 = ResidualBlock(32, 32)
        self.res52 = ResidualBlock(32, 32)

        self.linear = nn.Linear(32, 12, bias=True)

    def forward(self, x):
        # (B, 1024) -> (B, 1024, 1)
        x = x.unsqueeze(-1)

        x = self.dpt(self.res12(self.dpt(self.res1(self.act(self.bn1(self.conv1(x)))))))
        x = self.dpt(self.res22(self.dpt(self.res2(self.act(self.bn2(self.conv2(x)))))))
        x = self.dpt(self.res32(self.dpt(self.res3(self.act(self.bn3(self.conv3(x)))))))
        x = self.dpt(self.res42(self.dpt(self.res4(self.act(self.bn4(self.conv4(x)))))))
        x = self.dpt(self.res52(self.dpt(self.res5(self.act(self.bn5(self.conv5(x)))))))

        return self.linear(x.view(x.size(0), -1))

