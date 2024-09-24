import sys

import paramiko
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

class VLFair_SSH:
    def __init__(self, host='192.168.36.128', username='xxx', port=22, password='123456'):
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
    print(stdout.read())


def doSSHcmd(content):
    ssh_client = VLFair_SSH()
    ssh_client.connectSSH()
    #先清理上次的class和filter
    cmd = "sudo tc qdisc del dev ens33 root"
    runSSH(cmd,ssh_client)
    #再生成新的规则
    runSSH(content,ssh_client)
    ssh_client.closeSSH()

if __name__ == '__main__':

    cmd1 = "sudo tc qdisc del dev ens33 root"
    runSSH(cmd1)

