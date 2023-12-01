import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.elu = nn.ELU()
        self.batchnorm = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.elu(out)
        out = self.batchnorm(out)
        out = self.conv2(out)
        out = self.elu(out)
        out = self.batchnorm(out)
        out += residual
        return out


class EncoderBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(EncoderBlock, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=2, padding=1)
        self.elu = nn.ELU()
        self.batchnorm = nn.BatchNorm2d(out_channels)
        self.residual = ResidualBlock(out_channels, out_channels)

    def forward(self, x):
        out = self.conv(x)
        out = self.elu(out)
        out = self.batchnorm(out)
        out = self.residual(out)
        return out


class DecoderBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DecoderBlock, self).__init__()
        self.deconv = nn.ConvTranspose2d(in_channels, out_channels, kernel_size=3, stride=2, padding=1,
                                         output_padding=1)
        self.elu = nn.ELU()
        self.batchnorm = nn.BatchNorm2d(out_channels)
        self.residual = ResidualBlock(out_channels, out_channels)

    def forward(self, x, skip_connection):
        out = self.deconv(x)
        out = self.elu(out)
        out = self.batchnorm(out)

        # Ensure that skip_connection has the same number of channels as out
        # skip_connection = skip_connection[:, :out.size(1), :out.size(2), :out.size(3)]

        out += skip_connection
        out = self.residual(out)

        return out


class ConvolutionalAutoencoder(nn.Module):
    def __init__(self):
        super(ConvolutionalAutoencoder, self).__init__()

        # Encoder
        self.enc1 = EncoderBlock(3, 16)
        self.enc2 = EncoderBlock(16, 32)
        self.enc3 = EncoderBlock(32, 64)
        self.enc4 = EncoderBlock(64, 128)
        self.enc5 = EncoderBlock(128, 256)
        self.enc6 = EncoderBlock(256, 512)
        self.enc7 = EncoderBlock(512, 1024)

        # Decoder
        self.dec7 = DecoderBlock(1024, 512)
        self.dec6 = DecoderBlock(512, 256)
        self.dec5 = DecoderBlock(256, 128)
        self.dec4 = DecoderBlock(128, 64)
        self.dec3 = DecoderBlock(64, 32)
        self.dec2 = DecoderBlock(32, 16)
        self.dec1 = nn.ConvTranspose2d(16, 3, kernel_size=3, stride=2, padding=1,
                                       output_padding=1)

    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)
        e2 = self.enc2(e1)
        e3 = self.enc3(e2)
        e4 = self.enc4(e3)
        e5 = self.enc5(e4)
        e6 = self.enc6(e5)
        e7 = self.enc7(e6)

        # print(e7.size(), e6.size())

        # Decoder with skip connections
        d7 = self.dec7(e7, e6)
        d6 = self.dec6(d7, e5)
        d5 = self.dec5(d6, e4)
        d4 = self.dec4(d5, e3)
        d3 = self.dec3(d4, e2)
        d2 = self.dec2(d3, e1)
        out = self.dec1(d2)

        return e7, F.sigmoid(out)