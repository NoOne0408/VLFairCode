import pickle
import sys
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

FILE_PREFIX = 'VLFair/live_player_data/'

metrics = ['framesReceivedPerSecond', 'bitrate', 'frame_jitter', 'frameHeight']  # what to predict

estimation_methods = ['ip-udp-heuristic', 'rtp-heuristic', 'ip-udp-ml', 'rtp-ml']  # how to predict

dir_list = [
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/bitrate_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_1/',
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/framesReceivedPerSecond_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_2/',
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/frameHeight_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_1/',
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/frame_jitter_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_1/'
]


file_tuple = [
    FILE_PREFIX+'traffic_live.csv',
    FILE_PREFIX+'chrome-842_161_74_9_0_52_258-1684304046.json'
]


def load_intermediate(intermediates_dir):
    with open(f'{intermediates_dir}/model.pkl', 'rb') as fd:
        data_object = pickle.load(fd)
    return data_object


def predict_bitrate(dir):
    vca_model = load_intermediate(dir)
    model = vca_model['teams']
    output = model.estimate(file_tuple)
    return output[f'bitrate_gt']


def predict_framesReceivedPerSecond(dir):
    vca_model = load_intermediate(dir)
    model = vca_model['meet']
    output = model.estimate(file_tuple)
    return output[f'framesReceivedPerSecond_gt']


def predict_frameHeight(dir):
    vca_model = load_intermediate(dir)
    model = vca_model['meet']
    output = model.estimate(file_tuple)
    return output[f'frameHeight_gt']


def predict_frame_jitter(dir):
    vca_model = load_intermediate(dir)
    model = vca_model['meet']
    output = model.estimate(file_tuple)
    return output[f'frame_jitter_gt']


def predict(predictType):
    if predictType == 'bitrate':
        dir = dir_list[0]
        return predict_bitrate(dir)
    elif predictType == 'framesReceivedPerSecond':
        dir = dir_list[1]
        return predict_framesReceivedPerSecond(dir)
    elif predictType == 'frameHeight':
        dir = dir_list[2]
        return predict_frameHeight(dir)
    elif predictType == 'frame_jitter':
        dir = dir_list[3]
        return predict_frame_jitter(dir)


if __name__ == '__main__':
    print(predict('bitrate'))
    print(predict('framesReceivedPerSecond'))
    # print(predict('frameHeight'))
    print(predict('frame_jitter'))
