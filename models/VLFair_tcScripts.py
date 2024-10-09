import os
import sys
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

from models.VLFair_SSH import delete_tc_outer


PROXY_INGRESS = "wlp9s0"
PROXY_EGRESS = "vmnet1"
VM_INGRESS = "ens33"
MAX_BW = 6


# proxy入口限流，为了观察各个网络情况下的执行情况

def create_proxy_ingress_scripts(max_bw):
    print("createScriptsContentIngressProxy")
    script_tc = "sudo tc qdisc add dev " + PROXY_INGRESS + " handle ffff: ingress\n"
    script_tc += "sudo tc filter add dev " + PROXY_INGRESS + (" parent ffff: protocol ip prio 50 u32 match ip "
                                                              " src 0.0.0.0/0 police  rate ") + str(
        max_bw) + "mbit burst 10k drop\n"
    return script_tc


def show_proxy_ingress_scripts():
    script_tc = "sudo tc qdisc show dev " + PROXY_INGRESS + "\n"
    script_tc += "sudo tc filter show dev " + PROXY_INGRESS + " parent ffff:"
    return script_tc




# 将带宽结果转化为流控脚本内容
def create_proxy_egress_scripts(list_target_bw):
    print("createScriptsContentEgress")
    script_tc = "sudo tc qdisc add dev " + PROXY_EGRESS + " root handle 1: htb default 30 \n"
    classid = 1
    for bw in list_target_bw:
        script_tc += "sudo tc class add dev " + PROXY_EGRESS + " parent 1:0 classid 1:" + str(
            classid) + " htb rate " + str(bw) + "mbit\n"
        classid += 1
    # add filter
    script_tc += "sudo tc filter add dev " + PROXY_EGRESS + (" protocol ip parent 1:0 prio 1 u32 match ip "
                                                             " protocol 6 0xff match ip sport 80 0xffff "
                                                             " flowid 1:1 \n")
    script_tc += "sudo tc filter add dev " + PROXY_EGRESS + (" protocol ip parent 1:0 prio 1 u32 match ip "
                                                             " protocol 17 0xff match ip sport 8000 0xffff "
                                                             " flowid 1:2 \n")
    return script_tc


def show_proxy_egress_scripts():
    # show class and filter
    script_tc = "sudo tc class show dev " + PROXY_EGRESS + "\n"
    script_tc += "sudo tc filter show dev " + PROXY_EGRESS
    return script_tc


def create_vm_ingress_scripts(list_target_bw):
    print("createScriptsContentIngress")
    script_tc = "sudo tc qdisc add dev " + VM_INGRESS + " handle ffff: ingress\n"
    script_tc += "sudo tc filter add dev " + VM_INGRESS + (" parent ffff: protocol ip prio 1 u32 match ip "
                                                           " protocol 6 0xff match ip dport 80 0xffff police "
                                                           " rate ") + str(list_target_bw[0]) + "mbit burst 10k drop\n"
    script_tc += "sudo tc filter add dev " + VM_INGRESS + (" parent ffff: protocol ip prio 1 u32 match ip "
                                                           " protocol 17 0xff match ip dport 8000 0xffff police "
                                                           "rate ") + str(list_target_bw[1]) + "mbit burst 10k drop\n"
    return script_tc


def show_vm_ingress_scripts():
    script_tc = "sudo tc filter show dev " + VM_INGRESS + " parent ffff:"
    return script_tc


def doProxyEgressCommand(script_tc):
    delete_proxy_egress_scripts()
    os.system(script_tc)
    show_proxy_egress_scripts()

def delete_proxy_egress_scripts():
    cmd = "sudo tc qdisc del dev " + PROXY_EGRESS + " root"
    os.system(cmd)

def doProxyIngressCommand(script_tc):
    delete_proxy_ingress_scripts()
    os.system(script_tc)
    show_proxy_ingress_scripts()

def delete_proxy_ingress_scripts():
    cmd = "sudo tc qdisc del dev  " + PROXY_INGRESS + "  ingress"
    os.system(cmd)

def refresh_network_configuration():
    delete_proxy_ingress_scripts()
    delete_proxy_ingress_scripts()
    delete_tc_outer()


if __name__ == "__main__":
    refresh_network_configuration()
    script_tc = create_proxy_ingress_scripts(MAX_BW)
    doProxyIngressCommand(script_tc)


