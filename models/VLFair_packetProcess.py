from os.path import dirname, abspath
import sys
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

from models.VLFair_SSH import doSSHcmd
from models.VLFair_bandwidthCal import getBandwidthList
from models.VLFair_tcScripts import createScriptsContent
from models.VLFair_QoE_metrics_infer import getPlayerQoEMetrics, getPlayerQoE,getLivePlayerQoEMetrics
from models.VLFair_QoE_cal import getLivePlayerQoE,get_vod_metric_dic,getVodPlayerQoE



import subprocess
import threading
import socket
import json
import time
import os
import re
M_IN_K=1000
M_IN_BPS = 1000000
BIT_IN_BYTE = 8

# 创建两个条件变量
condition = threading.Condition()
t_vod_turn = True  # 标志线程1是否turn



FILE_PREFIX = 'VLFair/live_player_data/'

def getCoexistenceStatus():
    print("getCoexistenceStatus")
    m = 1
    n = 1
    total = 2
    return m,n,total

def doSomethingAfterCapture():
    print("im in doSomethingAfterCapture")

    # 1. 监听器，获取到这个时间段内共存的所有播放器情况：共存总个数，每个类别的player的个数
    m, n, total = getCoexistenceStatus()
    # 2. 获取到用于计算QoE的metric，区分vod和live
    list_vod, list_live=getPlayerQoEMetrics(m, n, total)
    # 3. 计算每个存活的player的QoE，返回结果是每个player的QoE
    getPlayerQoE(list_vod, list_live)
    # 4. 根据上述检测的参数和infer出来的Qoe，
    list_bw = getBandwidthList()
    # 5. 根据bw分配结果，返回tc脚本
    content = createScriptsContent(list_bw)
    # 6. 使用ssh执行脚本
    # doSSHcmd(content)




def parse_tshark(pcap_file,slot):
    # 构建 tshark 命令
    command = ['tshark', '-r', pcap_file, '-q', '-z', 'io,stat,'+str(slot)]

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

def get_vod_file(): 
    while True:
        print("circle_vod")
        file = FILE_PREFIX + 'captured_traffic_tcp.pcap'
        cmd = "sudo tshark -i vmnet1 -a duration:200 -f 'host 192.168.166.2 and tcp'  -w "+file
        os.system(cmd)

        
def get_live_file():
    while True:
        print("circle_live")
        file = FILE_PREFIX + 'captured_traffic.pcap'
        cmd = "sudo tshark -i vmnet1 -a duration:200 -f 'host 192.168.166.2 and udp' -w"  + file            
        os.system(cmd)

def print_tshark_output(pcap_file,time_gap):
    # 调用 subprocess 执行命令
    tshark_output = parse_tshark(pcap_file, time_gap)

    # 解析返回结果
    if tshark_output:
        # 解析输出并提取统计信息
        statistics = parse_tshark_output(tshark_output)
        # 打印提取的统计信息,every gap second
        for stat in statistics[-3:]:
            bitrate_per_gap_s = stat['bytes'] * BIT_IN_BYTE / M_IN_BPS
            bitrate = bitrate_per_gap_s / time_gap
            print(f"vod Interval: {stat['start_interval']} <> {stat['end_interval']}, "
                  f"Frames: {stat['frames']}, bitrate(mbps) : {bitrate}" + '\n')

last_chunk_quality = 0
def get_vod_status(data_dic):
    global last_chunk_quality
    # 要读取的 pcap 文件路径
    file = 'captured_traffic_tcp.pcap'
    pcap_file = FILE_PREFIX + file
    print_tshark_output(pcap_file,4)

    # print(f"buffer:{data_dic['buffer']}")        
    # print('last_chunk_quality_before:',last_chunk_quality)
    result_infer = get_vod_metric_dic(data_dic,last_chunk_quality)
    print('VOD result_infer:',result_infer)
    last_chunk_quality = data_dic['lastquality']
    # print('last_chunk_quality_after:',last_chunk_quality)
    qoe = getVodPlayerQoE(result_infer)
    print('VOD QoE:',qoe)


def get_live_status():
    while True:
        # 要读取的 pcap 文件路径
        file = 'captured_traffic.pcap'
        pcap_file = FILE_PREFIX + file
        csv_file = FILE_PREFIX + 'traffic_live.csv'

        cmd = 'sudo tshark -r '+pcap_file+' -T fields -e frame.number -e frame.time_relative -e frame.time_epoch -e ip.src -e ip.dst -e ip.proto -e ip.len -e udp.srcport -e udp.dstport -e udp.length -e rtp.ssrc -e rtp.timestamp -e rtp.seq -e rtp.p_type -e rtp.marker -E header=y -E separator=,> '+csv_file
        os.system(cmd)

        print_tshark_output(pcap_file, 4)

        print("live线程:数据获取完成")
        metrics = getLivePlayerQoEMetrics()
        # result = {'bitrate(mbps)':bitrate,'bitrate from ml (mbps)':metrics['bitrate'],'fps':metrics['fps'],'frame_jitter':metrics['frame_jitter'],'smoothness':metrics['smoothness']}
        # print(result)
        result_infer = {'bitrate':metrics['bitrate'],'framesReceivedPerSecond':metrics['fps'],'frame_jitter':metrics['frame_jitter'],'T_client':0,'T_server':0,'b_client':0,'smoothness':metrics['smoothness']}
        print('result_infer:',result_infer)
        qoe = getLivePlayerQoE(result_infer)
        print('Live QoE:',qoe)

        time.sleep(4)


# 定义监听的主机和端口
host = '0.0.0.0'  # 监听所有可用的网络接口
port = 8097  # 替换为实际端口

def get_buffer():
    # 创建一个TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 绑定到主机和端口
        s.bind((host, port))
        
        # 开始监听连接，允许最多 5 个未处理的连接
        s.listen(15)
        print(f"Server is listening on {host}:{port}")
        
        while True:
            try:
                # 等待客户端连接
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                
                # 为每个客户端连接创建新线程进行处理
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()

            except Exception as e:
                print(f"Error occurred: {e}")
                break
 


def handle_client(conn, addr):
    """处理每个客户端连接的函数"""
    with conn:
        try:
            while True: 
                    
                # 接收数据
                data = conn.recv(2048)
                if not data:
                    # print(f"Connection closed by {addr}")
                    break  # 客户端关闭连接时，退出循环
                # print(f"Received from {addr}: {data.decode('utf-8')}")
                data_dic = json.loads(data.decode('utf-8'))
                
                # event.set()  # 通知其他线程数据已获取
                print("vod线程：数据获取完成")
                

                get_vod_status(data_dic)
                
                # 发送响应（可选）
                response = "Message received"
                conn.sendall(response.encode('utf-8'))
           

        except Exception as e:
            print(f"Error with connection {addr}: {e}")
        # finally:
        #     print(f"Connection with {addr} closed")



def main():
    
    vod_file_thread = threading.Thread(target=get_vod_file)
    live_file_thread = threading.Thread(target=get_live_file)
    # vod_thread = threading.Thread(target=get_vod_status)
    live_thread = threading.Thread(target=get_live_status)
    # work_thread = threading.Thread(target=get_status)
    buffer_thread = threading.Thread(target=get_buffer)
    # buffer_thread.daemon = True  # 将线程设置为守护线程
    
    vod_file_thread.start()
    live_file_thread.start()
    # vod_thread.start()
    live_thread.start()
    # work_thread.start()
    buffer_thread.start()

    vod_file_thread.join()
    live_file_thread.join()
    # vod_thread.join()
    live_thread.join()
    # work_thread.join()
    buffer_thread.join()
     


if __name__ == "__main__":
    main()
