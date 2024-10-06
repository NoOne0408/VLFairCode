import math
import sys
from numpy import *
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

M_IN_K=1000
M_IN_BPS = 1000000

theta = 8.17
BPSTOMBPS=1000000
KBPSTOMBPS=1000

# 获取统计数据再赋值
rebuffer_max = 1
rebuffer_min = 0

frame_jitter_max = 1
frame_jitter_min = 0

latency_max = 1
latency_min = 0

VIDEO_BIT_RATE = [300,750,1200,1850,2850,4300]  # Kbps

# 标准化函数
def normalization_metrics(metric, value):
    result = 0
    if metric == 'rebuffer':
        result = (value - rebuffer_min) / rebuffer_max
    elif metric == 'frame_jitter':
        result = (value - frame_jitter_min) / frame_jitter_max
    else:
        result = (value - latency_min) / latency_max
    return result


# 用户体验系数向量定义，分别代表着质量、重缓冲、质量切换、端到端延迟,PQ, rebuffer, smoothness, latency
qoe_vector = [[1, -1, -1, 0],
              [1, 0, -1, 0]]
def get_live_rebuffer(fps, x, bufferold):
    return 0


def get_live_smoothness(bitrate_items):
    last_PQ = 0
    smoothness_list = []
    for item in  bitrate_items:
        PQ = get_live_normalization_PQ(item/M_IN_BPS)
        PQ_gap = abs(PQ-last_PQ)
        smoothness_list.append(PQ_gap)
        last_PQ = PQ
         
    smoothness = mean(smoothness_list)
    return smoothness


def get_live_frame_jitter(frame_jitter):
    return frame_jitter

# 获取端到端延迟
def get_end2end_latency(T_client, T_server, b_client):
    # print('获取live端到端延迟')
    return abs(T_client - T_server + b_client)

def get_live_normalization_PQ(bitrate):
    # print('获取live标准化质量指标')
    q = 1 - math.exp(-theta * bitrate)
    return q

def get_live_normalization_rebuffer(fps, x, bufferold):
    # print('获取live标准化重缓冲指标')
    return normalization_metrics('rebuffer', get_live_rebuffer(fps, x, bufferold))

def get_live_normalization_frame_jitter(frame_jitter):
    # print('获取live标准化质量切换指标')
    return normalization_metrics('frame_jitter', get_live_frame_jitter(frame_jitter))

def get_live_normalization_latency(T_client, T_server, b_client):
    # print('获取live标准化端到端延迟指标')
    return normalization_metrics('latency', get_end2end_latency(T_client, T_server, b_client))



def calLivePlayerQoE(live_metrics):
    PQ = get_live_normalization_PQ(live_metrics['bitrate'])
    rebuffer=get_live_normalization_rebuffer(live_metrics['framesReceivedPerSecond'],0,0)
    smoothness = live_metrics['smoothness']
    latency = get_live_normalization_latency(live_metrics['T_client'], live_metrics['T_server'], live_metrics['b_client'])
    frame_jitter = get_live_normalization_frame_jitter(live_metrics['frame_jitter'])
    qoe = qoe_vector[1][0] * PQ + qoe_vector[1][1] * rebuffer + qoe_vector[1][2] * smoothness + qoe_vector[1][3]*latency
    # print('live qoe and metrics(qoe,PQ,rebuffer,smoothness,latency,frame_jitter):',qoe,PQ,rebuffer,smoothness,latency,frame_jitter)
    return qoe



# vod metrics
# 获取重缓冲时长 , bw的值为1/x
def get_vod_rebuffer(size, x, bufferold):
    # print('获取重缓冲时长(正数)')
    rebuffer_time = abs(size * x - bufferold)
    return rebuffer_time

# 获取质量切换次数
def get_vod_smoothness(q_now, q_old):
    # print('获取质量切换')
    return abs(q_now - q_old)


# 获取某个播放器某时隙 k 用户体验指标
def get_vod_normalization_PQ(bitrate):
    # print('获取vod标准化质量指标')
    # bitrate = bitrate / KBPSTOMBPS
    q = 1 - math.exp(-theta * bitrate)
    return q

def get_vod_normalization_rebuffer(size, x, bufferold):
    # print('获取vod标准化重缓冲指标')
    return normalization_metrics('rebuffer', get_vod_rebuffer(size, x, bufferold))


def get_vod_normalization_smoothess(q_now, q_old):
    # print('获取vod标准化质量切换指标')
    pq_now = get_vod_normalization_PQ(q_now)
    pq_old = get_vod_normalization_PQ(q_old)
    return normalization_metrics('smoothness', get_vod_smoothness(pq_now, pq_old))



# 获取某个vod播放器某时隙 k 用户体验值
def calVodPlayerQoE(vod_metrics):
    # print('获取质量QoE')
    PQ = get_vod_normalization_PQ(vod_metrics['bitrate'])
    rebuffer = vod_metrics['RebufferTime']
    # rebuffer = get_vod_normalization_rebuffer(vod_metrics['size'], vod_metrics['x'], vod_metrics['bufferold'])
    smoothness = get_vod_normalization_smoothess(vod_metrics['q_now'], vod_metrics['q_old'])
    qoe = qoe_vector[0][0] * PQ + qoe_vector[0][1] * rebuffer + qoe_vector[0][2] * smoothness
    print('vod qoe and metrics:',qoe,PQ,rebuffer,smoothness)
    return qoe

def get_vod_metric_dic(data_dic,last_chunk_quality):
    # rebuffer:ms
    result_infer = {'bitrate':VIDEO_BIT_RATE[data_dic['lastquality']]/M_IN_K,
    'RebufferTime':data_dic['RebufferTime']/ M_IN_K,
    'q_now':VIDEO_BIT_RATE[data_dic['lastquality']]/ M_IN_K,
    'q_old':VIDEO_BIT_RATE[last_chunk_quality]/ M_IN_K}
    return result_infer

if __name__ == '__main__':
    print(get_vod_normalization_PQ(100))
    print(get_live_normalization_PQ(0.1))