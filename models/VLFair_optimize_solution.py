import sys

import numpy as np
from scipy.optimize import linprog
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)
# 最优化问题求解，需要目标函数，约束条件，以及要确定有多少个求解变量，有n个vod和m个live
# 目标函数 max fx = QoE_sum(Xn), 转化为最小值问题，并获取系数矩阵
# 不等式约束参数矩阵
#     1. 网络约束
#     2. 公平性约束（另一个目标转化而成）
# 不等式约束参数向量
#     1. 网络带宽最大值：B
#     2. 公平从约束最大值
# X1-n的取值范围：X1〉0……Xn〉0


def get_Object_param(n, m):
    print('获取目标函数的参数向量')
    list1 = []
    for i in range(n + m):
        list1.append(-1)
    print("c", list1)
    return list1


def get_constrain_matrix(n, m):
    print('获取不等式约束参数矩阵(获取网络参数 向量,获取公平性参数 向量)')

    list1 = []
    for i in range(n + m):
        list1.append(1)

    list2 = []
    for i in range(n + m):
        list2.append(1)

    list_total = []
    list_total.append(list1)
    list_total.append(list2)

    print("A_ub", list_total)

    return list_total


def get_constrain_vector(BW, a):
    print('获取不等式约束参数 向量')
    list1 = []
    list1.append(BW)
    list1.append(a)
    print("B_ub", list1)
    return list1


def get_A_eq_param(n, m):
    print('获取等式参数向量')
    list_total = []
    list1 = []
    for i in range(n + m):
        list1.append(1)
    list_total.append(list1)
    print("A_eq", list_total)
    return list_total


def get_x_range(n, m, BW):
    print('X1-n的取值范围：X1〉0……Xn〉0')
    list1 = []
    for i in range(n + m):
        t = (0, BW)
        list1.append(t)
    print("bounds", tuple(list1))
    return tuple(list1)


n = 10
m = 10
BW = 10  # 10mbps
a = 0.1  # Jain fairness param
c = np.array(get_Object_param(n, m))
A_ub = np.array(get_constrain_matrix(n, m))
B_ub = np.array(get_constrain_vector(BW, a))
A_eq = np.array(get_A_eq_param(n, m))
B_eq = np.array([BW])
t = get_x_range(n, m, BW)

res = linprog(c, A_ub, B_ub, A_eq, B_eq, bounds=t)
print(res)