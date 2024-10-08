import numpy as np

from models.VLFair_log_module import get_all_records, divide_records_dic_by_type, get_records_by_type
import matplotlib.pyplot as plt

SCHEMES = ['vod', 'live']

dict_qoe = {}
dict_PQ = {}
dict_rebuffer = {}
dict_smoothness = {}
dict_latency = {}
dict_bandwidth_before = {}
dict_bandwidth_after = {}
dict_timestamp = {}


def init_data_list():
    for scheme in SCHEMES:
        dict_qoe[scheme] = []
        dict_PQ[scheme] = []
        dict_rebuffer[scheme] = []
        dict_smoothness[scheme] = []
        dict_latency[scheme] = []
        dict_bandwidth_before[scheme] = []
        dict_bandwidth_after[scheme] = []
        dict_timestamp[scheme] = []


def injerk_data(file):
    records_list = get_all_records(file)
    records_dic = divide_records_dic_by_type(records_list)

    for scheme in SCHEMES:
        records_scheme = get_records_by_type(scheme, records_dic)
        timestamp_init = int(records_scheme[0]['timestamp'])
        for record in records_scheme:
            qoe = float(record['qoe'])
            if qoe < 0: continue
            dict_qoe[scheme].append(qoe)
            dict_PQ[scheme].append(float(record['PQ']))
            dict_rebuffer[scheme].append(float(record['rebuffer']))
            dict_smoothness[scheme].append(float(record['smoothness']))
            dict_latency[scheme].append(float(record['latency']))
            dict_bandwidth_before[scheme].append(float(record['bw_before']))
            dict_bandwidth_after[scheme].append(float(record['bw_after']))
            dict_timestamp[scheme].append(int(record['timestamp']) - timestamp_init)

        print('dict_qoe', type(float(dict_qoe[scheme][0])))


COLOR_MAP = plt.cm.jet  # nipy_spectral, Set1,Paired

fig = plt.figure(figsize=(16, 8))


def plot_qoe():
    ax = fig.add_subplot(111)
    for scheme in SCHEMES:
        ax.plot(dict_timestamp[scheme], dict_qoe[scheme])
    colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(ax.lines))]
    for i, j in enumerate(ax.lines):
        j.set_color(colors[i])
    # plt.title(l)
    plt.ylabel('qoe')

    plt.xlabel('time (sec)')

    SCHEMES_REW = []
    for scheme in SCHEMES:
        SCHEMES_REW.append('QoE' + ': ' + scheme)

    # 输出reward
    ax.legend(SCHEMES_REW, loc=8, bbox_to_anchor=(0.5, -0.1), ncol=int(np.ceil(len(SCHEMES) / 2.0)))
    # plt.savefig(RESULTS_IMAGE_FOLDER+l+'.jpg')
    # plt.gca().invert_yaxis()
    plt.show()

def plot_bw():
    ax = fig.add_subplot(111)

    for scheme in SCHEMES:
        ax.plot(dict_timestamp[scheme], dict_bandwidth_before[scheme])
    for scheme in SCHEMES:
        ax.plot(dict_timestamp[scheme], dict_bandwidth_after[scheme])
    colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(ax.lines))]
    for i, j in enumerate(ax.lines):
        j.set_color(colors[i])
    # plt.title(l)
    plt.ylabel('bandwidth')

    plt.xlabel('time (sec)')

    SCHEMES_REW = []
    for scheme in SCHEMES:
        SCHEMES_REW.append('BW' + ': ' + scheme)

    # 输出reward
    ax.legend(SCHEMES_REW, loc=8, bbox_to_anchor=(0.5, -0.1), ncol=int(np.ceil(len(SCHEMES) / 2.0)))
    # plt.savefig(RESULTS_IMAGE_FOLDER+l+'.jpg')
    # plt.gca().invert_yaxis()
    plt.show()

if __name__ == "__main__":
    init_data_list()
    injerk_data('regulation_on.log')
    # plot_qoe()
    plot_bw()