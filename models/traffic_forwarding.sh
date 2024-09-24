# 无限循环
while true; do
    # 开启转发规则
    sudo iptables -t nat -A PREROUTING -s 192.168.166.2 -p udp --dport 8000 -j REDIRECT --to-port 8001

    echo "Traffic forwarding enabled."

    # 等待一小段时间（例如0.5秒）以便捕获并转发流量
    sleep 5

    # 关闭转发规则
    sudo iptables -t nat -D PREROUTING -s 192.168.166.2 -p udp --dport 8000 -j REDIRECT --to-port 8001
    echo "Traffic forwarding disabled."

    # 等待 5 秒钟
    sleep 5
done
