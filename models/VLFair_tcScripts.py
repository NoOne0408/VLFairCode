import os
import sys
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

folder = ""


# 将流控脚本内容输出到脚本文件中
# def createScripts(content):
#     file_name = "VLFair/traffic_control.sh"
#     path = floder + file_name
#     with open(path, "w") as file:
#         file.write(content)

# 将带宽结果转化为流控脚本内容
def createScriptsContentEgress(list_target_bw):
    print("createScriptsContentEgress")
    host_network_interfare = "vmnet1"
    script_tc = "sudo tc qdisc add dev " + host_network_interfare + " root handle 1: htb default 30 \n"
    classid = 1
    for bw in list_target_bw:
        script_tc += "sudo tc class add dev " + host_network_interfare + " parent 1:0 classid 1:" + str(
            classid) + " htb rate " + str(bw) + "mbit\n"
        classid += 1
    # add filter
    script_tc += "sudo tc filter add dev " + host_network_interfare + (" protocol ip parent 1:0 prio 1 u32 match ip "
                                                                       " protocol 6 0xff match ip sport 80 0xffff "
                                                                       " flowid 1:1 \n")
    script_tc += "sudo tc filter add dev " + host_network_interfare + (" protocol ip parent 1:0 prio 1 u32 match ip "
                                                                       " protocol 17 0xff match ip sport 8000 0xffff "
                                                                       " flowid 1:2 \n")

    # show class and filter
    script_tc += "sudo tc class show dev " + host_network_interfare + "\n"
    script_tc += "sudo tc filter show dev " + host_network_interfare
    return script_tc


def createScriptsContentIngress(list_target_bw):
    network_interfare = "ens33"
    print("createScriptsContentIngress")
    script_tc = "sudo tc qdisc add dev " + network_interfare + " handle ffff: ingress\n"
    script_tc += "sudo tc filter add dev " + network_interfare + (" parent ffff: protocol ip prio 1 u32 match ip "
                                                                  " protocol 6 0xff match ip dport 80 0xffff police "
                                                                  " rate ") + str(list_target_bw[0]) + "mbit burst 10k drop\n"
    script_tc += "sudo tc filter add dev " + network_interfare + (" parent ffff: protocol ip prio 1 u32 match ip "
                                                                  " protocol 17 0xff match ip dport 8000 0xffff police "
                                                                  "rate ") + str(list_target_bw[1]) + "mbit burst 10k drop\n"
    script_tc += "sudo tc filter show dev " + network_interfare + " parent ffff:"
    return script_tc


def doEgressCommand(script_tc):
    cmd = "sudo tc qdisc del dev vmnet1 root"
    os.system(cmd)
    os.system(script_tc)


if __name__ == "__main__":
    list_target_bw = [1, 2]
    content = createScriptsContentEgress(list_target_bw)
    print(content)
    # content = "sudo tc qdisc del dev vmnet1 root"
    doEgressCommand(content)
