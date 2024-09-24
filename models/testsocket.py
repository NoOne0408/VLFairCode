import socket
import select

# 代理服务器监听的端口
PROXY_PORT = 8000
# 目标服务器（本地 Apache）的地址和端口
TARGET_HOST = '127.0.0.1'
TARGET_PORT = 80

# 创建一个socket对象，用于监听客户端连接
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy_socket.bind(('0.0.0.0', PROXY_PORT))
proxy_socket.listen(100)

# 存储所有连接的字典
connections = {}

print(f"Proxy server is listening on port {PROXY_PORT}...")

try:
    while True:
        # 使用select模块等待事件
        readable, writable, errored = select.select([proxy_socket] + list(connections.keys()), [], [])

        for s in readable:
            if s is proxy_socket:
                # 新客户端连接
                client_socket, client_address = proxy_socket.accept()
                print(f"Accepted connection from {client_address}")

                # 创建连接到目标服务器
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_socket.connect((TARGET_HOST, TARGET_PORT))

                # 在connections字典中保存客户端socket和目标服务器socket的对应关系
                connections[client_socket] = target_socket
                connections[target_socket] = client_socket

            else:
                # 处理已经存在的连接
                data = s.recv(4096)
                if data:
                    # 从一个socket读取数据并发送到它对应的另一个socket
                    connections[s].send(data)
                else:
                    # 如果没有数据，意味着连接已经关闭，清理资源
                    print(f"Closing connection {s.getpeername()}")
                    partner_socket = connections[s]
                    partner_socket.close()
                    s.close()
                    del connections[partner_socket]
                    del connections[s]

finally:
    # 关闭代理服务器的socket
    proxy_socket.close()
