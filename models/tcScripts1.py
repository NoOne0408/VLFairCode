# import bandwidthCal
# import models.predictTest1
# from  vcaml.src.models import  predictTest1
import predictLiveMetrics


floder = ""
host_network_interfare = "ens33"

def createScripts(content):
    file_name = "traffic_control.sh"
    path = floder + file_name
    with open(path, "w") as file:
        file.write(content)

def createScriptsContent(list_bw):
    script_tc = "sudo tc qdisc add dev ens33 root handle 1: htb default 30 \n"
    classid = 1
    for bw in list_bw:
        script_tc += "sudo tc class add dev " + host_network_interfare + " parent 1:0 classid 1:" + str(
            classid) + " htb rate " + str(bw) + "mbps\n"
        classid = classid + 1
    script_tc += "sudo tc class show dev ens33\n"
    script_tc += "sudo tc filter show dev ens33"
    return script_tc


def calBandwidth():
    return 1, 3


def doSomethingAfterCapture():
    print("im in doSomethingAfterCapture")
    # 输出对应的带宽计算结果，并增加到list中
    print(calBandwidth())
    bw1, bw2 = calBandwidth()
    list_bw = []
    list_bw.append(bw1)
    list_bw.append(bw2)
    # 将带宽结果转化为流控脚本内容
    content = createScriptsContent(list_bw)
    print(content)
    # 将流控脚本内容输出到脚本文件中
    # print(createScripts(content))
    #
    # print(bandwidthCal.liveQoE())
    print(predictLiveMetrics.predict('bitrate'))

print(predictLiveMetrics.predict('bitrate'))