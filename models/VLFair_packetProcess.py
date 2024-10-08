import threading
import time
import sys
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

from models.VLFair_tcScripts import create_proxy_egress_scripts, create_vm_ingress_scripts, doProxyEgressCommand
from models.VLFair_listener import listen_main, getCoexistenceStatus
from models.VLFair_bandwidthCal import getBandwidthList, getCalBandwidthList
from models.VLFair_log_module import getRegulationContent, doWrite
from models.VLFair_SSH import doSSHcmd


def regulationAfterListening():
    while True:
        print("im in doSomethingAfterListen")

        # 1. 监听器，获取到这个时间段内共存的所有播放器情况：共存总个数，每个player的qoe和metric指标
        list_qoe = getCoexistenceStatus()
        print('list_qoe:', list_qoe)
        # 2. 获取每个player的bw占用量
        list_bw = getBandwidthList()
        print('list_bw:', list_bw)

        try:
            # 3. 获取每个player的target bw
            list_target_bw = getCalBandwidthList(list_bw, list_qoe)
            print('list_target_bw:', list_target_bw)

            # 4. log
            regulation_content = getRegulationContent(list_qoe, list_bw, list_target_bw)
            doWrite('regulation.log', regulation_content)

            # 5. 根据bw分配结果，返回tc脚本
            content_egress = create_proxy_egress_scripts(list_target_bw)
            print('content_egress:', content_egress)

            content_ingress = create_vm_ingress_scripts(list_target_bw)
            print('content_ingress:', content_ingress)

            #  6. proxy执行egress tc, vm执行ingress tc (ssh)
            # doProxyEgressCommand(content_egress)
            # do_ssh_cmd_result = doSSHcmd(content_ingress)
            # print('doSSHcmd:', do_ssh_cmd_result)
        except Exception as e:
            print(f"xxxtest try catch")

        time.sleep(3)


if __name__ == "__main__":
    listen_main()
    regulation_thread = threading.Thread(target=regulationAfterListening)
    regulation_thread.start()
    regulation_thread.join()
