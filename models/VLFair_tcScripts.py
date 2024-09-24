import sys
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

floder = ""
host_network_interfare = "ens33"

# 将流控脚本内容输出到脚本文件中
# def createScripts(content):
#     file_name = "VLFair/traffic_control.sh"
#     path = floder + file_name
#     with open(path, "w") as file:
#         file.write(content)

# 将带宽结果转化为流控脚本内容
def createScriptsContent(list_bw):
    print("createScriptsContent")
    script_tc = "sudo tc qdisc add dev ens33 root handle 1: htb default 30 \n"
    classid = 1
    for bw in list_bw:
        script_tc += "sudo tc class add dev " + host_network_interfare + " parent 1:0 classid 1:" + str(
            classid) + " htb rate " + str(bw) + "mbps\n"
        classid = classid + 1
    script_tc += "sudo tc class show dev ens33\n"
    script_tc += "sudo tc filter show dev ens33"
    return script_tc



#2. 根据上述返回结果，计算出bandwidth
# def getBandwidthList():
#     print("getBandwidthList")
#     bw1, bw2 = 3, 3
#     list_bw = []
#     list_bw.append(bw1)
#     list_bw.append(bw2)
#     return list_bw


















