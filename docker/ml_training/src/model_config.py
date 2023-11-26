from collections import OrderedDict


def get_config():

    n_c = 16

    # ENCODER CONFIG
    encoder_config = OrderedDict()

    # (3, 256, 256) -> (16, 128, 128)
    encoder_config['conv1'] = {'in': 1, 'out': n_c, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu', 'bn': True}

    # # (16, 128, 128) -> (16, 128, 128)
    encoder_config['conv2'] = {'in': n_c, 'out': n_c, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu', 'bn': True}

    # 16,128,128 -> 32,64,64
    encoder_config['conv3'] = {'in': n_c, 'out': n_c*2, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu', 'bn': True}
    encoder_config['conv3.5'] = {'in': n_c*2, 'out': n_c * 2, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu',
                               'bn': True}
    # 32,64,64 -> 64,32,32
    encoder_config['conv4'] = {'in': n_c*2,  'out': n_c * 4, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                               'bn': True}
    encoder_config['conv4.5'] = {'in': n_c * 4, 'out': n_c * 4, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu',
                               'bn': True}
    # 64,32,32 -> 128,16,16
    encoder_config['conv5'] = {'in': n_c * 4, 'out': n_c * 8, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                               'bn': True}
    encoder_config['conv5.5'] = {'in': n_c * 8, 'out': n_c * 8, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu',
                               'bn': True}
    # 128,16,16 -> 256,8,8
    encoder_config['conv6'] = {'in': n_c * 8, 'out': n_c * 16, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                               'bn': True}
    # 256,8,8 -> 512,4,4
    encoder_config['conv7'] = {'in': n_c * 16, 'out': n_c * 32, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                               'bn': True}
    # 512,4,4 -> 1024,2,2
    encoder_config['conv8'] = {'in': n_c * 32, 'out': n_c * 64, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                               'bn': True}
    # 1024,2,2 -> GAP (1034,1,1)
    encoder_config['avg_pool2d'] = {}
    encoder_config['flatten'] = {}

    # DECODER CONFIG

    decoder_config = OrderedDict()

    decoder_config['reshape'] = {'in': n_c * 64, 'out': (n_c * 64, 1, 1)}
    # 1024,1,1 -> 1024,2,2
    decoder_config['deconv1'] = {'in': n_c*64, 'out':n_c*64, 'ksize':3, 'stride':2, 'padding':1, 'act':'elu', 'bn':True, 'output_padding':1}
    # 1024,2,2 -> 512,4,4
    decoder_config['deconv2'] = {'in': n_c * 64, 'out': n_c * 32, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                                 'bn': True, 'output_padding':1}
    # 512,4,4 -> 256,8,8
    decoder_config['deconv3'] = {'in': n_c * 32, 'out': n_c * 16, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                                 'bn': True, 'output_padding':1}
    # 256,8,8 -> 128,16,16
    decoder_config['deconv4'] = {'in': n_c * 16, 'out': n_c * 8, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                                 'bn': True, 'output_padding':1}
    decoder_config['conv1'] = {'in': n_c * 8, 'out': n_c * 8, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu',
                                 'bn': True}
    # 128,16,16 -> 64,32,32
    decoder_config['deconv5'] = {'in': n_c * 8, 'out': n_c * 4, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                                 'bn': True, 'output_padding':1}
    decoder_config['conv2'] = {'in': n_c * 4, 'out': n_c * 4, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu',
                                 'bn': True}
    # 64,32,32 -> 32,64,64
    decoder_config['deconv6'] = {'in': n_c * 4, 'out': n_c * 2, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                                 'bn': True, 'output_padding':1}
    decoder_config['conv3'] = {'in': n_c * 2, 'out': n_c * 2, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu',
                                 'bn': True}
    # 32,64,64 -> 16,128,128
    decoder_config['deconv7'] = {'in': n_c * 2, 'out': n_c, 'ksize': 3, 'stride': 2, 'padding': 1, 'act': 'elu',
                                 'bn': True, 'output_padding':1}
    decoder_config['conv4'] = {'in': n_c, 'out': n_c, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu',
                                 'bn': True}
    decoder_config['conv5'] = {'in': n_c, 'out': n_c, 'ksize': 3, 'stride': 1, 'padding': 1, 'act': 'elu',
                               'bn': True}
    decoder_config['deconv9'] = {'in': n_c, 'out': 1, 'ksize': 3, 'stride': 2, 'padding': 1, 'bn': True,
                                 'output_padding':1}

    sample_config = {
        'encoder': encoder_config,
        'decoder': decoder_config
    }

    return sample_config
