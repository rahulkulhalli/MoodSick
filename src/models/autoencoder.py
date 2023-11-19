import torch.nn as nn


class MultiModalEncoder(nn.Module):
    def __init__(self, im_size: int, config: dict):
        super(MultiModalEncoder, self).__init__()
        self.im_size = im_size
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
                bias=False
            )
        )
        if config['act'] == 'relu':
            layers.append(nn.ReLU(inplace=False))
        elif config['act'] == 'lrelu':
            layers.append(nn.LeakyReLU(negative_slope=0.01, inplace=False))
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
        if config['act'] == 'relu':
            layers.append(nn.ReLU(inplace=False))
        elif config['act'] == 'lrelu':
            layers.append(nn.LeakyReLU(negative_slope=0.01, inplace=False))
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
        if 'act' in config:
            if config['act'] == 'relu':
                layers.append(nn.ReLU(inplace=False))
            elif config['act'] == 'lrelu':
                layers.append(nn.LeakyReLU(negative_slope=0.01, inplace=False))

        return nn.Sequential(*layers)

    def _flatten(self):
        return nn.Sequential(nn.Flatten())

    def _reshape(self, config: dict):
        return nn.Sequential(nn.Unflatten(dim=1, unflattened_size=config['out']))

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

        return decoder

    def forward(self, im):

        # Pass through the encoder.
        for module in self.encoder:
            im = module(im)

        # Obtain a reference to the bottleneck.
        x = im

        # Pass through the decoder.
        for module in self.decoder:
            im = module(im)

        return x, im
