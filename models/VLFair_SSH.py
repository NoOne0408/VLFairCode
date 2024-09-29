import sys

import paramiko
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

class VLFair_SSH:
    def __init__(self, host='192.168.166.2', username='xxx', port=22, password='123456'):
        self.ip = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None

    def closeSSH(self):
        self.connection.close()
    def connectSSH(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if self.password != '':
                self.connection.connect(self.ip, self.port, self.username, (str(self.password)), timeout=15.0)
            else:
                try:
                    self.connection.connect(self.ip, self.port, self.username, look_for_keys=False,
                                            allow_agent=False, timeout=5.0)
                except paramiko.ssh_exception.SSHException:
                    self.connection.get_transport().auth_none(self.username)
                    self.connection.exec_command('uname -a')
                self.connection.sftp = paramiko.SFTPClient.from_transport(self.connection.get_transport())
        except Exception as e:
            try:
                print(str(e.args))
                self.connection = None
            finally:
                e = None
                del e

def runSSH(cmd,ssh_client):
    # 执行命令并获取命令结果
    stdin, stdout, stderr = ssh_client.connection.exec_command(cmd)
    return stdout.read()
    # print(stdout.read())


def doSSHcmd(content):
    print('doSSHcmd')
    ssh_client = VLFair_SSH()
    ssh_client.connectSSH()
    #先清理上次的class和filter
    cmd = "sudo tc qdisc del dev ens33 root"
    runSSH(cmd,ssh_client)
    #再生成新的规则
    return_content = runSSH(content,ssh_client)
    ssh_client.closeSSH()
    return return_content


if __name__ == '__main__':
    cmd1 = "sudo tc qdisc add dev ens33 root handle 1: htb default 30\n"
    cmd2 = "sudo tc class add dev ens33 parent 1:0 classid 1:1 htb rate 1mbit\n"
    cmd3 = "sudo tc class add dev ens33 parent 1:0 classid 1:2 htb rate 5mbit\n"
    cmd4 = "sudo tc filter add dev ens33 protocol ip parent 1:0 prio 1 u32 match ip dst 127.0.0.1 match ip dport 80 0xffff flowid 1:1\n"
    cmd5 = "sudo tc filter add dev ens33 protocol ip parent 1:0 prio 2 u32 match ip dst 127.0.0.1 match ip dport 80 0xffff flowid 1:2\n"
    cmd6 = "sudo tc class show dev ens33\n"
    cmd7 =  "sudo tc filter show dev ens33\n"
    cmd = cmd1+cmd2+cmd3+cmd4+cmd5+cmd6+cmd7

    # cmd = "sudo tc qdisc del dev ens33 root"
    doSSHcmd(cmd)

