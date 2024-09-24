import time
from os.path import dirname, abspath
import sys
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

from models.VLFair_SSH import doSSHcmd
from models.VLFair_bandwidthCal import getBandwidthList
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
        qoe_list = getCoexistenceStatus()
        print(qoe_list)
        # 2. 获取每个player的bw占用量
        list_bw = getBandwidthList()
        print(list_bw)

        # 5. 根据bw分配结果，返回tc脚本
        # content = createScriptsContent(list_bw)
        # 6. 使用ssh执行脚本
        # doSSHcmd(content)
        time.sleep(3)
     


if __name__ == "__main__":
    main()
    dosomething_thread = threading.Thread(target=doSomethingAfterListen)
    dosomething_thread.start()
    dosomething_thread.join()
