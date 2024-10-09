import re
import subprocess
import sys
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__)))
sys.path.append(d)
from numpy import *

from VLFair_tcScripts import MAX_BW

M_IN_K = 1000
M_IN_BPS = 1000000
BIT_IN_BYTE = 8
FILE_PREFIX = 'VLFair/live_player_data/'


def getBandwidthList():
    print("getBandwidthList")
    list_bw = []
    dic_vod = {'type': 'vod', 'bw': print_vod_output()}
    dic_live = {'type': 'live', 'bw': print_live_output()}
    list_bw.append(dic_vod)
    list_bw.append(dic_live)
    return list_bw


# 最简单的带宽分配方式：按照本player的QoE占总QoE的比值去分配带宽，qoe越小分配到的带宽越多
def getCalBandwidthList(list_bw, list_qoe):
    try:
        print("getCalBandwidthList")
        qoe_value_list = get_qoe_value_list(list_qoe)
        bandwidth_value_list = get_bandwidth_value_list(list_bw)

        total_bandwidth = sum(bandwidth_value_list)
        # total_bandwidth = MAX_BW
        target_bandwidth_list = []
        i = 0

        for qoe in qoe_value_list:
            # qoe_ratio = get_qoe_ratio(qoe, qoe_value_list)
            qoe_ratio = get_qoe_ratio_oppose(qoe, qoe_value_list)
            bw_new = total_bandwidth*qoe_ratio
            # print('qoe_ratio',qoe_ratio)
            # bw_new = cal_bw_by_qoe(bandwidth_value_list[i], total_bandwidth, qoe_ratio)
            i += 1
            target_bandwidth_list.append(bw_new)
        return target_bandwidth_list
    except Exception as e:
        print(f"xxxtest getCalBandwidthList:{e}")


def cal_bw_by_qoe(bw, bw_total, qoe_ratio):
    new_bw = bw_total/2
    # if qoe_ratio < 0.5:
    #     new_bw = min(bw * 2, bw_total)
    # elif qoe_ratio > 0.5:
    #     new_bw = bw / 2
    return new_bw


def get_qoe_ratio(qoe, qoe_list):
    return qoe / sum(qoe_list)


def get_qoe_ratio_oppose(qoe, qoe_list):
    return 1 - (qoe / sum(qoe_list))


# 将字典转化为只包含bw数值的list
def get_bandwidth_value_list(list_bw):
    bandwidth_value_list = []
    for bw_dic in list_bw:
        # player_key = list(bw_dic.keys())[0]
        bw = bw_dic['bw']
        # print('bw_value', bw)
        bandwidth_value_list.append(bw)
    return bandwidth_value_list


# 将字典转化为只包含 qoe数值的list
def get_qoe_value_list(list_qoe):
    qoe_value_list = []
    for qoe_dict in list_qoe:
        # player_key = list(qoe_dict.keys())[0]
        qoe_value = qoe_dict['qoe']
        # print('qoe_value',qoe_value)
        qoe_value_list.append(qoe_value)
    return qoe_value_list


def parse_tshark(pcap_file, slot):
    # 构建 tshark 命令
    command = ['tshark', '-r', pcap_file, '-q', '-z', 'io,stat,' + str(slot)]

    # 调用 subprocess 执行命令
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error running tshark: {result.stderr}")
        return None

    return result.stdout


def parse_tshark_output(output):
    # 初始化存储解析结果的列表
    statistics = []

    # 匹配统计数据的正则表达式模式
    # 例如：在如下行中提取时间段、Frames 和 Bytes:
    # |  0 <> 1  |   1661 | 2301299 |
    pattern = re.compile(r"\|\s*(\d+(?:\.\d+)?)\s*<>\s*(\d+(?:\.\d+)?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|")

    # 逐行解析输出
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            # 提取时间段、帧数和字节数
            start_interval = match.group(1)
            end_interval = match.group(2)
            frames = int(match.group(3))
            bytes_ = int(match.group(4))

            # 存储解析结果
            statistics.append({
                'start_interval': start_interval,
                'end_interval': end_interval,
                'frames': frames,
                'bytes': bytes_
            })

    return statistics


def print_tshark_output(pcap_file, time_gap, type):
    # 调用 subprocess 执行命令
    tshark_output = parse_tshark(pcap_file, time_gap)

    # 解析返回结果
    if tshark_output:

        # 解析输出并提取统计信息
        statistics = parse_tshark_output(tshark_output)
        if statistics:
            # 打印提取的统计信息,every gap second
            bitrate_list = []
            for stat in statistics[-3:]:
                bitrate_per_gap_s = stat['bytes'] * BIT_IN_BYTE / M_IN_BPS
                bitrate = bitrate_per_gap_s / time_gap
                bitrate_list.append(bitrate)
                # print(type+f" Interval: {stat['start_interval']} <> {stat['end_interval']}, "
                #       f"Frames: {stat['frames']}, bitrate(mbps) : {bitrate}" + '\n')
            return mean(bitrate_list)
        else:
            return 0


def print_vod_output():
    # 要读取的 pcap 文件路径
    file = 'captured_traffic_tcp.pcap'
    pcap_file = FILE_PREFIX + file
    time_gap = 4
    return print_tshark_output(pcap_file, time_gap, 'vod')


def print_live_output():
    # 要读取的 pcap 文件路径
    file = 'captured_traffic.pcap'
    pcap_file = FILE_PREFIX + file
    time_gap = 4
    return print_tshark_output(pcap_file, time_gap, 'live')


if __name__ == "__main__":
    list_bw = getBandwidthList()
    print(list_bw)
