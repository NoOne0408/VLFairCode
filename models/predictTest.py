import os
import pickle
from itertools import product

from models.config import project_config
from util.data_splitter import KfoldCVOverFiles
from util.file_processor import FileProcessor


def load_intermediate(intermediates_dir):
    with open(f'{intermediates_dir}/model.pkl', 'rb') as fd:
        data_object = pickle.load(fd)
    return data_object


def predict(dir):
    vca_model = load_intermediate(dir)
    file_tuple = [
        '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data/2023-05-16_meet_842_161_74_9_0_52_258/meet-chrome-842_161_74_9_0_52_258-1684303978.csv',
        '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data/2023-05-16_meet_842_161_74_9_0_52_258/chrome-842_161_74_9_0_52_258-1684304046.json']
    model = vca_model['meet']
    output = model.estimate(file_tuple)
    # print(output[f'framesReceivedPerSecond_gt'])
    # print(output[f'frameHeight_gt'])
    # print(output[f'frame_jitter_gt'])
    print(output[f'bitrate_gt'])


if __name__ == '__main__':
    # metrics = ['framesReceivedPerSecond', 'bitrate',
    #            'frame_jitter', 'frameHeight']  # what to predict
    # estimation_methods = ['ip-udp-heuristic', 'rtp-heuristic', 'ip-udp-ml', 'rtp-ml']  # how to predict
    #
    # param_list = [metrics, estimation_methods]
    #
    # dir = '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/framesReceivedPerSecond_rtp-ml_LSTATS-TSTATS_in_lab_data_cv_3/'
    # vca_model = load_intermediate(dir)
    #
    # data_dir = ['/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data']
    #
    # bname = os.path.basename(data_dir[0])
    # intermediates_dir = f'{data_dir[0]}_intermediates'
    #
    # fp = FileProcessor(data_directory=data_dir[0])
    # file_dict = fp.get_linked_files()
    #
    # kcv = KfoldCVOverFiles(5, file_dict, project_config, bname)
    # file_splits = kcv.split()
    #
    # with open(f'{intermediates_dir}/cv_splits.pkl', 'wb') as fd:
    #     pickle.dump(file_splits, fd)

    # for fsp in file_splits:
    #     for vca in fsp:
    #         print(vca)
    #         for file_tuple in fsp[vca]['test']:
    #             print(file_tuple)
    #             model = vca_model[vca]
    #             output = model.estimate(file_tuple)
    #
    #             print(output[f'framesReceivedPerSecond_gt'])
    #             break
    #         break
    #     break

    # dir = '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/framesReceivedPerSecond_ip-udp-ml_LSTATS-TSTATS_in_lab_data_cv_2/'
    # dir = '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/frameHeight_ip-udp-ml_LSTATS-TSTATS_in_lab_data_cv_1/'
    # dir = '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/frame_jitter_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_1/'
    dir = '/home/xxx/PycharmProjects/pythonProjectvcmal/vcaml/data/in_lab_data_intermediates/bitrate_ip-udp-heuristic_LSTATS-TSTATS_in_lab_data_cv_1/'
    predict(dir)
