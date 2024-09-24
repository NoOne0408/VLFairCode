 
#TPROXY_BIND_PORT = 8000
def tcp_listener(bind_ip, port,real_dest):
    # 创建监听 socket
    print("test tcp")
    listener_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener_fd.setsockopt(socket.SOL_IP, socket.IP_TRANSPARENT, 1)
    listener_fd.bind((bind_ip, port))
    listener_fd.listen(10)


    while True:
        client_sock, client_addr = listener_fd.accept()
        captured_addr = client_sock.getsockname()

         

        print(f"Listening on port {port}, you think you are talking to {real_dest}, actually you are captured by {captured_addr}")
        

        # 连接到原始目的地
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            remote_sock.connect(real_dest)
            # print('connecting to remote')

        except socket.error as e:
            print(f"Error connecting to original destination: {e}")
            client_sock.close()
            continue

        # 在客户端和目标服务器之间转发数据
        try:
            while True:
                # doSomethingAfterCapture()
                # 从客户端接收数据并转发给原始服务器
                data = client_sock.recv(1024)
                
                if not data:
                    print("not data")
                    break
                # print(f"Forwarding data to {real_dest}: {data[:100]}")
                remote_sock.sendall(data)

                # 从原始服务器接收响应并转发回客户端
                response = b''
                while True:
                    part = remote_sock.recv(1024)
                    if not part:
                        break
                    response += part 
                    print('part.decode()',part[:100])

                if not response:
                    print("not response")
                    break
                print(f"Forwarding response to client total: {response[:100]}")    
                client_sock.sendall(response)
                

                


        except socket.error as e:
            print(f"Error during data forwarding: {e}")

        # 关闭连接
        client_sock.close()
        remote_sock.close()
    
def get_vod_csv():
    os.system(
            'sudo tshark -r VLFair/live_player_data/captured_traffic_tcp.pcap -T fields -e frame.number -e frame.time_relative -e frame.time_epoch -e ip.src -e ip.dst -e ip.proto -e ip.len -e udp.srcport -e udp.dstport -e udp.length -e rtp.ssrc -e rtp.timestamp -e rtp.seq -e rtp.p_type -e rtp.marker -E header=y -E separator=,> VLFair/live_player_data/traffic_vod.csv')

    df = pd.read_csv('VLFair/live_player_data/traffic_vod.csv')
    print(df)    


def udp_listener(bind_ip, port,real_dest):
    print("test udp")
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((bind_ip, port))
    
    while True:
        
        # 接收数据包
        data, client_addr = udp_sock.recvfrom(4096)
        print(data[:10])
        print(f"Listening on port {port}, you think you are talking to {real_dest}, actually you are captured by 192.168.166.1:{port}")

        # 转发数据包到原始目的地
        udp_sock.sendto(data, real_dest)
        #print(f"Forwarded data to {real_dest}")

        # 接收目标服务器的响应
        response, _ = udp_sock.recvfrom(4096)
        #print(f"Received response from {real_dest}: {response}")

        # 将响应发送回客户端
        udp_sock.sendto(response, client_addr)
        #print(f"Forwarded response to {client_addr}")

def main():
    bind_ip_tcp = '0.0.0.0'
    port_tcp = 8000
    real_dest_tcp = ('10.129.28.27',80)
    tcp_thread = threading.Thread(target=tcp_listener, args=(bind_ip_tcp, port_tcp, real_dest_tcp))
    
     
    
    # bind_ip_udp = '0.0.0.0'
    # port_udp = 8001
    # real_dest_udp = ('10.129.28.27',8000)
    # udp_thread = threading.Thread(target=udp_listener, args=(bind_ip_udp, port_udp, real_dest_udp))
    
    # tcp_thread.start()
    # udp_thread.start()

    # tcp_thread.join()
    # udp_thread.join()
     