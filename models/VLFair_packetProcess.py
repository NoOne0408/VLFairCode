import time
from os.path import dirname, abspath
import sys
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

from models.VLFair_SSH import doSSHcmd
from models.VLFair_bandwidthCal import getBandwidthList, getCalBandwidthList
from models.VLFair_tcScripts import createScriptsContent
from models.VLFair_listener import main, getCoexistenceStatus

import threading



# 创建两个条件变量
condition = threading.Condition()
t_vod_turn = True  # 标志线程1是否turn


def doSomethingAfterListen():
    while True:
        print("im in doSomethingAfterListen")

        # 1. 监听器，获取到这个时间段内共存的所有播放器情况：共存总个数，每个player的qoe和metric指标
        list_qoe = getCoexistenceStatus()
        print('list_qoe:',list_qoe)
        # 2. 获取每个player的bw占用量
        list_bw = getBandwidthList()
        print('list_bw:',list_bw)

        try:
            # 3. 获取每个player的target bw
            list_target_bw = getCalBandwidthList(list_bw,list_qoe)
            print('list_target_bw:',list_target_bw)

            # 5. 根据bw分配结果，返回tc脚本
            content = createScriptsContent(list_target_bw)
            print('content:',content)
            # 6. 使用ssh执行脚本
            doSSHcmd_result = doSSHcmd(content)
            print('doSSHcmd:',doSSHcmd_result)
        except Exception as e:
            print(f"xxxtest try catch")

        time.sleep(3)
     


if __name__ == "__main__":
    main()
    dosomething_thread = threading.Thread(target=doSomethingAfterListen)
    dosomething_thread.start()
    dosomething_thread.join()
