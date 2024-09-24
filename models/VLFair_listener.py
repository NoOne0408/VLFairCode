import threading
import socket
import json
import time
import os

from os.path import dirname, abspath
import sys
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

from models.VLFair_QoE_metrics_infer import getLivePlayerQoEMetrics
from models.VLFair_QoE_cal import getLivePlayerQoE,get_vod_metric_dic,getVodPlayerQoE
FILE_PREFIX = 'VLFair/live_player_data/'


live_qoe_dic={}
vod_qoe_dic={}

def getCoexistenceStatus():
    print("getCoexistenceStatus")
    # m = 1
    # n = 1
    # total = 2
    qoe_list = []
    qoe_list.append(vod_qoe_dic)
    qoe_list.append(live_qoe_dic)
    return qoe_list


def get_vod_file():
    while True:
        print("circle_vod")
        file = FILE_PREFIX + 'captured_traffic_tcp.pcap'
        cmd = "sudo tshark -i vmnet1 -a duration:200 -f 'host 192.168.166.2 and tcp'  -w " + file
        os.system(cmd)


def get_live_file():
    while True:
        print("circle_live")
        file = FILE_PREFIX + 'captured_traffic.pcap'
        cmd = "sudo tshark -i vmnet1 -a duration:200 -f 'host 192.168.166.2 and udp' -w" + file
        os.system(cmd)


last_chunk_quality = 0


def get_vod_status(data_dic):
    global vod_qoe_dic
    global last_chunk_quality

    # print(f"buffer:{data_dic['buffer']}")
    # print('last_chunk_quality_before:',last_chunk_quality)
    result_infer = get_vod_metric_dic(data_dic, last_chunk_quality)
    # print('VOD result_infer:', result_infer)
    last_chunk_quality = data_dic['lastquality']
    # print('last_chunk_quality_after:',last_chunk_quality)
    qoe = getVodPlayerQoE(result_infer)
    # print('VOD QoE:', qoe)
    vod_qoe_dic = {'vod qoe':qoe}


def get_live_status():
    global live_qoe_dic
    while True:
        # 要读取的 pcap 文件路径
        file = 'captured_traffic.pcap'
        pcap_file = FILE_PREFIX + file
        csv_file = FILE_PREFIX + 'traffic_live.csv'

        cmd = 'sudo tshark -r ' + pcap_file + ' -T fields -e frame.number -e frame.time_relative -e frame.time_epoch -e ip.src -e ip.dst -e ip.proto -e ip.len -e udp.srcport -e udp.dstport -e udp.length -e rtp.ssrc -e rtp.timestamp -e rtp.seq -e rtp.p_type -e rtp.marker -E header=y -E separator=,> ' + csv_file
        os.system(cmd)

        # print_tshark_output(pcap_file, 4)

        print("live线程:数据获取完成")
        metrics = getLivePlayerQoEMetrics()
        # result = {'bitrate(mbps)':bitrate,'bitrate from ml (mbps)':metrics['bitrate'],'fps':metrics['fps'],'frame_jitter':metrics['frame_jitter'],'smoothness':metrics['smoothness']}
        # print(result)
        result_infer = {'bitrate': metrics['bitrate'], 'framesReceivedPerSecond': metrics['fps'],
                        'frame_jitter': metrics['frame_jitter'], 'T_client': 0, 'T_server': 0, 'b_client': 0,
                        'smoothness': metrics['smoothness']}
        # print('result_infer:', result_infer)
        qoe = getLivePlayerQoE(result_infer)
        # print('Live QoE:', qoe)

        live_qoe_dic = {'live qoe':qoe}

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
    live_thread = threading.Thread(target=get_live_status)
    buffer_thread = threading.Thread(target=get_buffer)
    # buffer_thread.daemon = True  # 将线程设置为守护线程

    vod_file_thread.start()
    live_file_thread.start()
    live_thread.start()
    buffer_thread.start()

    # vod_file_thread.join()
    # live_file_thread.join()
    # live_thread.join()
    # buffer_thread.join()

if __name__ == "__main__":
    main()