
import sys
import os
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import socket
import time



from pathlib import Path, PureWindowsPath

num_retries = 10
path = 'C:\\ETCS2-TRK_TestEnv_93B\\Simu\\MooN_Simu\\RBC5\\'
path = path + 'Config'
VBoxPath = "C:\\Program Files\\Oracle\\VirtualBox\\"
RBCName = 'RBC5_93B'


if os.path.exists(path):
    print('ok')
else:
    print('ko')

os.chdir(VBoxPath)

print("Current working directory: {0}".format(os.getcwd()))

#response = os.system('VBoxManage.exe startvm '+ RBCName +' --type headless')



client = SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#client.load_host_keys()
retry = 0
while retry < num_retries:
    try:
        client.connect(hostname='192.168.56.3', port=22, username='imp_gateway', password='imp_gateway',  timeout=5)
        #client.connect(hostname='192.168.56.55', port=22, username='admin', password='admin',  timeout=5)
        scp = SCPClient(client.get_transport())
        retry = num_retries
    except Exception as inst:
        print(inst)
        time.sleep(5)
        retry += 1

winpath = PureWindowsPath(path)

correct_path = Path(winpath)

print(correct_path)

stdin, stdout, stderr = client.exec_command('ls')
print(stdout)

sout = stdout.read().decode("utf8")

if (len(sout) != 0):
            # print(stdout.read().decode("utf8"))
    print('STDOUT: ' + sout)
serr = stderr.read().decode("utf8")

if (len(serr) != 0):
            # print(stderr.read().decode("utf8"))
    print( f'STDERR: ' + serr)
#scp.put(path, recursive=True, remote_path='/MooNSimu/LDS')
