import sys
import math
import predictTest1

from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)
from models.VLFair_QoE_cal import  get_live_normalization_PQ, get_live_smoothness
M_IN_K=1000
M_IN_BPS = 1000000
BIT_IN_BYTE = 8


#1. 根据live中间文件，获取到QoE以及metric
def getPlayerQoEMetrics(m, n, total):
    print("getPlayerQoEMetrics")
    list_vod = []
    list_live = []
    return list_vod, list_live




def getLivePlayerQoEMetrics():
    # print("getLivePlayerQoEMetrics")
    metrics = ['bitrate', 'framesReceivedPerSecond', 'frame_jitter']  # what to predict
    bitrate_origin = predictTest1.predict(metrics[0]).mean()    
    smoothness = get_live_smoothness(predictTest1.predict(metrics[0]))
    fps = predictTest1.predict(metrics[1]).mean()
    frame_jitter = predictTest1.predict(metrics[2]).mean()
    live_metrics = {'bitrate':bitrate_origin/M_IN_BPS,'fps': fps, 'frame_jitter': frame_jitter, 'smoothness':smoothness}
    # print(live_metrics)
    return live_metrics
def getVodPlayerQoEMetrics():
    print("getVodPlayerQoEMetrics")
    vod_metrics = {'bitrate': 100, 'size': 0, 'x': 0, 'bufferold': 0, 'q_now': 0, 'q_old': 0}
    return vod_metrics

def getPlayerQoE(list_vod, list_live):
    print("getPlayerQoE")
    pass

if __name__ == '__main__':
    vod_metrics = getVodPlayerQoEMetrics()
    live_metrics =getLivePlayerQoEMetrics()


