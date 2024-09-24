
import sys
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

import pickle

dir_list = [
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/bitrate_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_1/',
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/framesReceivedPerSecond_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_2/',
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/frameHeight_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_1/',
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/frame_jitter_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_1/'
]

metrics = ['framesReceivedPerSecond', 'bitrate', 'frame_jitter', 'frameHeight']  # what to predict

estimation_methods = ['ip-udp-heuristic', 'rtp-heuristic', 'ip-udp-ml', 'rtp-ml']  # how to predict

# file_tuple = [
#     '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data/2023-05-16_meet_842_161_74_9_0_52_258/meet-chrome-842_161_74_9_0_52_258-1684303978.csv',
#     '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data/2023-05-16_meet_842_161_74_9_0_52_258/chrome-842_161_74_9_0_52_258-1684304046.json']

# file_tuple = [
#     '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/src/models/VLFair/live_player_data/traffic_live.csv',
#     '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/src/models/VLFair/live_player_data/traffic_live.json'
# ]

file_tuple = [
    '/home/xxx/VLFair/models/VLFair/live_player_data/traffic_live.csv',
    '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data/2023-05-16_meet_842_161_74_9_0_52_258/chrome-842_161_74_9_0_52_258-1684304046.json'
]


def load_intermediate(intermediates_dir):
    with open(f'{intermediates_dir}/model.pkl', 'rb') as fd:
        data_object = pickle.load(fd)
    return data_object


def predict_bitrate(dir, file_tuple):
    vca_model = load_intermediate(dir)
    model = vca_model['teams']
    output = model.estimate(file_tuple)
    # print(output)
    return output[f'bitrate_gt']
    # print(output[f'bitrate_gt'])


def predict_framesReceivedPerSecond(dir, file_tuple):
    vca_model = load_intermediate(dir)
    model = vca_model['meet']
    output = model.estimate(file_tuple)
    return output[f'framesReceivedPerSecond_gt']
    # print(output[f'framesReceivedPerSecond_gt'])


def predict_frameHeight(dir, file_tuple):
    vca_model = load_intermediate(dir)
    model = vca_model['meet']
    output = model.estimate(file_tuple)
    return output[f'frameHeight_gt']
    # print(output[f'frameHeight_gt'])


def predict_frame_jitter(dir, file_tuple):
    vca_model = load_intermediate(dir)
    model = vca_model['meet']
    output = model.estimate(file_tuple)
    return output[f'frame_jitter_gt']
    # print(output[f'frame_jitter_gt'])


def predict(predictType):
    if predictType == 'bitrate':
        dir = dir_list[0]
        return predict_bitrate(dir, file_tuple)
    elif predictType == 'framesReceivedPerSecond':
        dir = dir_list[1]
        return predict_framesReceivedPerSecond(dir, file_tuple)
    elif predictType == 'frameHeight':
        dir = dir_list[2]
        return predict_frameHeight(dir, file_tuple)
    elif predictType == 'frame_jitter':
        dir = dir_list[3]
        return predict_frame_jitter(dir, file_tuple)


if __name__ == '__main__':
    print(predict('bitrate'))
    print(predict('framesReceivedPerSecond'))
    # print(predict('frameHeight'))
    print(predict('frame_jitter'))
