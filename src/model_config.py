from collections import OrderedDict


def get_config():
    # ENCODER CONFIG
    encoder_config = OrderedDict()

    encoder_config['conv1'] = {'in': 3, 'out': 8, 'ksize': 5, 'padding': 1, 'stride': 2, 'act': 'relu'}
    encoder_config['conv2'] = {'in': 8, 'out': 8, 'ksize': 3, 'padding': 1, 'stride': 1, 'act': 'relu'}
    encoder_config['conv3'] = {'in': 8, 'out': 16, 'ksize': 3, 'padding': 1, 'stride': 2, 'act': 'relu'}
    encoder_config['conv4'] = {'in': 16, 'out': 16, 'ksize': 3, 'padding': 1, 'stride': 1, 'act': 'relu'}
    encoder_config['conv5'] = {'in': 16, 'out': 32, 'ksize': 3, 'padding': 1, 'stride': 2, 'act': 'relu'}
    encoder_config['conv6'] = {'in': 32, 'out': 32, 'ksize': 3, 'padding': 1, 'stride': 1, 'act': 'relu'}
    encoder_config['conv7'] = {'in': 32, 'out': 64, 'ksize': 3, 'padding': 1, 'stride': 2, 'act': 'relu'}
    encoder_config['conv8'] = {'in': 64, 'out': 64, 'ksize': 3, 'padding': 1, 'stride': 1, 'act': 'relu'}
    encoder_config['conv9'] = {'in': 64, 'out': 128, 'ksize': 3, 'padding': 1, 'stride': 2, 'act': 'relu'}
    encoder_config['conv10'] = {'in': 128, 'out': 128, 'ksize': 3, 'padding': 1, 'stride': 1, 'act': 'relu'}
    encoder_config['flatten'] = {}
    encoder_config['linear1'] = {'in': 9856, 'out': 512, 'bias': True, 'act': 'relu'}


    # DECODER CONFIG

    decoder_config = OrderedDict()

    # torch.Size([8, 3, 220, 336])
    # torch.Size([8, 8, 109, 167])
    # torch.Size([8, 8, 109, 167])
    # torch.Size([8, 16, 55, 84])
    # torch.Size([8, 16, 55, 84])
    # torch.Size([8, 32, 28, 42])
    # torch.Size([8, 32, 28, 42])
    # torch.Size([8, 64, 14, 21])
    # torch.Size([8, 64, 14, 21])
    # torch.Size([8, 128, 7, 11])
    # torch.Size([8, 128, 7, 11])
    # torch.Size([8, 9856])

    decoder_config['linear1'] = {'in': 512, 'out': 9856, 'bias': True, 'acr': 'relu'}
    decoder_config['reshape'] = {'in': 9856, 'out': (128, 7, 11)}
    decoder_config['deconv1'] = {'in': 128, 'out': 128, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'relu'}
    decoder_config['deconv2'] = {'in': 128, 'out': 64, 'ksize': 3, 'stride': 2, 'padding': 1, 'output_padding': 1, 'act': 'relu'}
    decoder_config['deconv3'] = {'in': 64, 'out': 64, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'relu'}
    decoder_config['deconv4'] = {'in': 64, 'out': 32, 'ksize': 3, 'stride': 2, 'padding': 1, 'output_padding': 1, 'act': 'relu'}
    decoder_config['deconv5'] = {'in': 32, 'out': 32, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'relu'}
    decoder_config['deconv6'] = {'in': 32, 'out': 16, 'ksize': 3, 'stride': 2, 'padding': 1, 'output_padding': 1, 'act': 'relu'}
    decoder_config['deconv7'] = {'in': 16, 'out': 16, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'relu'}
    decoder_config['deconv8'] = {'in': 16, 'out': 8, 'ksize': 3, 'stride': 2, 'padding': 1, 'output_padding': 1, 'act': 'relu'}
    decoder_config['deconv9'] = {'in': 8, 'out': 8, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'relu'}
    decoder_config['deconv10'] = {'in': 8, 'out': 3, 'ksize': 3, 'stride': 2, 'padding': 1, 'output_padding': 1, 'act': 'relu'}

    sample_config = {
        'encoder': encoder_config,
        'decoder': decoder_config
    }

    return sample_config