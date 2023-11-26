import torch.nn as nn
import torch.nn.functional as F


class MultiModalEncoder(nn.Module):
    def __init__(self, config: dict):
        super(MultiModalEncoder, self).__init__()
        self.config = config
        self.encoder = self._make_encoder()
        self.decoder = self._make_decoder()

    def _conv_block(self, config: dict):
        layers = list()
        layers.append(
            nn.Conv2d(
                in_channels=config['in'],
                out_channels=config['out'],
                padding=config['padding'],
                kernel_size=config['ksize'],
                stride=config['stride'],
                bias=config['bias'] if 'bias' in config else False
            )
        )

        if 'bn' in config and config['bn']:
            layers.append(nn.BatchNorm2d(config['out']))

        if 'act' in config:
            if config['act'] == 'relu':
                layers.append(nn.ReLU(inplace=True))
            elif config['act'] == 'lrelu':
                layers.append(nn.LeakyReLU(negative_slope=0.01, inplace=True))
            elif config['act'] == 'sigmoid':
                layers.append(nn.Sigmoid())
            elif config['act'] == 'elu':
                layers.append(nn.ELU(alpha=1.0, inplace=True))
        return nn.Sequential(*layers)

    def _deconv_block(self, config: dict):
        layers = list()
        layers.append(
            nn.ConvTranspose2d(
                in_channels=config['in'],
                out_channels=config['out'],
                padding=config['padding'],
                kernel_size=config['ksize'],
                output_padding=config['output_padding'] if 'output_padding' in config else 0,
                stride=config['stride'],
                bias=False
            )
        )

        if 'bn' in config and config['bn']:
            layers.append(nn.BatchNorm2d(config['out']))

        if 'act' in config:
            if config['act'] == 'relu':
                layers.append(nn.ReLU(inplace=True))
            elif config['act'] == 'lrelu':
                layers.append(nn.LeakyReLU(negative_slope=0.01, inplace=True))
            elif config['act'] == 'sigmoid':
                layers.append(nn.Sigmoid())
            elif config['act'] == 'elu':
                layers.append(nn.ELU(alpha=1.0, inplace=True))
        return nn.Sequential(*layers)

    def _linear(self, config: dict):
        layers = list()
        layers.append(
            nn.Linear(
                in_features=config['in'],
                out_features=config['out'],
                bias=config['bias']
            )
        )

        if 'bn' in config and config['bn']:
            layers.append(nn.BatchNorm2d(config['out']))

        if 'act' in config:
            if config['act'] == 'relu':
                layers.append(nn.ReLU(inplace=True))
            elif config['act'] == 'lrelu':
                layers.append(nn.LeakyReLU(negative_slope=0.01, inplace=True))
            elif config['act'] == 'elu':
                layers.append(nn.ELU(alpha=1.0, inplace=True))

        return nn.Sequential(*layers)

    def _flatten(self):
        return nn.Sequential(nn.Flatten())

    def _avgpool(self):
        return nn.Sequential(nn.AdaptiveAvgPool2d(output_size=(1, 1)))

    def _reshape(self, config: dict):
        return nn.Sequential(nn.Unflatten(dim=1, unflattened_size=config['out']))

    def _mpool(self):
        return nn.Sequential(nn.MaxPool2d(kernel_size=(2, 2)))

    def _upsample(self):
        return nn.Sequential(nn.Upsample(scale_factor=2, mode='bilinear'))

    def _make_encoder(self):
        encoder_config = self.config['encoder']
        encoder = nn.ModuleList()

        for layer_type, config in encoder_config.items():
            if 'conv' in layer_type:
                encoder.append(self._conv_block(config))
            elif 'linear' in layer_type:
                encoder.append(self._linear(config))
            elif 'flatten' in layer_type:
                encoder.append(self._flatten())
            elif 'avg_pool2d' in layer_type:
                encoder.append(self._avgpool())
            elif 'mpool' in layer_type:
                encoder.append(self._mpool())

        return encoder

    def _make_decoder(self):
        decoder_config = self.config['decoder']
        decoder = nn.ModuleList()

        for layer_type, config in decoder_config.items():
            if 'linear' in layer_type:
                decoder.append(self._linear(config))
            elif 'reshape' in layer_type:
                decoder.append(self._reshape(config))
            elif 'deconv' in layer_type:
                decoder.append(self._deconv_block(config))
            elif 'conv' in layer_type and 'de' not in layer_type:
                # CONV layer.
                decoder.append(self._conv_block(config))
            elif 'upsample' in layer_type:
                decoder.append(self._upsample())

        return decoder

    def forward(self, im):

        # Pass through the encoder.
        for module in self.encoder:
            im = module(im)
            # print('enc: ', im.size())

        # Obtain a reference to the bottleneck.
        x = im

        # Pass through the decoder.
        for module in self.decoder:
            im = module(im)
            # print('dec: ', im.size())

        return x, F.sigmoid(im)
