import socket
import struct
TPROXY_BIND_PORT = 8000

 


def get_original_dst(sock):
    SO_ORIGINAL_DST = 80  # 在 Linux 上，SO_ORIGINAL_DST 的值通常为 80
    orig_dst = sock.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
    ip, port = struct.unpack_from("!4sH", orig_dst, 0)
    ip = socket.inet_ntoa(ip)
    port = socket.ntohs(port)
    return (ip, port)

def main():
    # 创建监听 socket
    listener_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener_fd.setsockopt(socket.SOL_IP, socket.IP_TRANSPARENT, 1)
    listener_fd.bind(('0.0.0.0', TPROXY_BIND_PORT))
    listener_fd.listen(10)

    print(f"Listening on port {TPROXY_BIND_PORT}")

    while True:
        client_sock, client_addr = listener_fd.accept()

        # # 获取客户端的目标地址
        # intended_dest_addr = client_sock.getsockname()
        # print(f"Accepted connection from {client_addr}, intended destination {intended_dest_addr}")

        real_dest = ('10.129.28.27',80)

        # 连接到原始目的地
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            remote_sock.connect(real_dest)

        except socket.error as e:
            print(f"Error connecting to original destination: {e}")
            client_sock.close()
            continue

        # 在客户端和目标服务器之间转发数据
        try:
            while True:
                # 从客户端接收数据并转发给原始服务器
                data = client_sock.recv(1024)
                
                if not data:
                    print("not data")
                    break
                print(f"Forwarding data to {real_dest}: {data[:100]}")
                remote_sock.sendall(data)

                # 从原始服务器接收响应并转发回客户端
                response = b''
                while True:
                    part = remote_sock.recv(1024)
                    if not part:
                        break
                    response += part 
                if not response:
                    print("not response")
                    break
                print(f"Forwarding response to client: {response[:100]}")
                client_sock.sendall(response)
        except socket.error as e:
            print(f"Error during data forwarding: {e}")

        # 关闭连接
        client_sock.close()
        remote_sock.close()

if __name__ == "__main__":
    main()
