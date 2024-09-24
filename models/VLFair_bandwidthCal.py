import re
import subprocess
import sys
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)
from numpy import *


M_IN_K=1000
M_IN_BPS = 1000000
BIT_IN_BYTE = 8
FILE_PREFIX = 'VLFair/live_player_data/'

def getBandwidthList():
    print("getBandwidthList")
    list_bw = []
    list_bw.append(print_vod_output())
    list_bw.append(print_live_output())
    return list_bw

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

def print_tshark_output(pcap_file, time_gap,type):
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
    return print_tshark_output(pcap_file, time_gap,'vod')

def print_live_output():
    # 要读取的 pcap 文件路径
    file = 'captured_traffic.pcap'
    pcap_file = FILE_PREFIX + file
    time_gap = 4
    return print_tshark_output(pcap_file, time_gap,'live')

if __name__ == "__main__":
    list_bw = getBandwidthList()
    print(list_bw)