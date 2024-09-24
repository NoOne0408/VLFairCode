import sys
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)
# def getBandwidthList():
#     print("getBandwidthList")
#     bw_list = {}
#     return bw_list

def getBandwidthList():
    print("getBandwidthList")
    bw1, bw2 = 3, 3
    list_bw = []
    list_bw.append(bw1)
    list_bw.append(bw2)
    return list_bw