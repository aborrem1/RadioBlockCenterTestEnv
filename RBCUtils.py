import paramiko
from datetime import datetime
from paramiko import SSHClient
from scp import SCPClient

import socket
import sys
import os
import subprocess
import time


DefaultPort = 22
Defaultuser = 'admin'
Defaultpassword = 'admin'
Hostvmadapteraddr = '192.168.56.101'

num_retries = 10

VBoxPath = 'C:\\Program Files\\Oracle\\VirtualBox\\'

timeformat = "%Y%m%d_%H%M%S.%f: "


class RBCUtils:

    def __init__(self, workingDir, RBCVersion, RBCName,  RBCip, RBCport = DefaultPort, RBCuser = Defaultuser, RBCpass = Defaultpassword):
        self._client = SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._workingDir = workingDir
        self._RBCVersion = RBCVersion
        self._RBCName = RBCName
        self._RBCip = RBCip
        self._RBCport = RBCport
        self._RBCuser = RBCuser
        self._RBCpass = RBCpass


        # Change the current working directory
        #os.chdir(self._workingDir)


    def sendCmd(self, cmds):
        stdin, stdout, stderr = self._client.exec_command(cmds)
        now = datetime.now()

        sout = stdout.read().decode("utf8")

        if (len(sout) != 0):
            # print(stdout.read().decode("utf8"))
            print(now.strftime(timeformat) + 'STDOUT: ' + sout)

        serr = stderr.read().decode("utf8")

        if (len(serr) != 0):
            # print(stderr.read().decode("utf8"))
            print(now.strftime(timeformat) + f'STDERR: ' + serr)

        # if stderr.channel.recv_exit_status() != 0:
        #     print("The following error occured:" + str(stderr.readlines()))
        # print(stdout.readlines())


    def log(self, message):
        now = datetime.now()
        print(now.strftime(timeformat) + str(message))


    def StartRBCOnHost(self):

        self._client.connect(self._RBCip, port=self._RBCport,  username=self._RBCuser, password=self._RBCpass)
        scp = SCPClient(self._client.get_transport())

        cmds = f'sudo chmod -R 777 /MooNSimu/LDS/Executables'
        self.sendCmd(cmds)

        scp.put(self._workingDir + "Config", recursive=True, remote_path='/MooNSimu/LDS') #"./Config"

        #print(self._workingDir + "Config\\")

        scp.put(self._workingDir + 'Executables', recursive=True, remote_path='/MooNSimu/LDS') #'./Executables'
        scp.put(self._workingDir + 'MooN_Simu.conf', recursive=True, remote_path='/home/admin/LDS_BSL5.5')
        #scp.put('check.sh', recursive=True, remote_path='/home/admin/LDS_BSL5.5/')
        scp.put(self._workingDir + 'SCU.gid', recursive=True, remote_path='/home/admin/LDS_BSL5.5/Gid/')

        cmds = f'sudo chmod -R 777 /MooNSimu/LDS/Executables'
        self.sendCmd(cmds)

        cmds = f'sudo chmod -R 777 /MooNSimu/LDS/Config'
        self.sendCmd(cmds)

        cmds = f'sudo chmod -R 777 /home/admin/LDS_BSL5.5/*'
        self.sendCmd(cmds)

        self.log("Starting the MooN Simulator of " + self._RBCName)

        cmds = f'/home/admin/LDS_BSL5.5/start_moon_simu.sh'
        self.sendCmd(cmds)
        #TODO: check if return if different of:
        #/home/admin/LDS_BSL5.5/start_moon_simu.sh: line 283:  1639 Aborted                 (core dumped) /MooNSimu/LDS/Executables/mooncore-cb $ARG_CH $ARG_NVRAM $ARG_SACEM_MASK1 $ARG_SACEM_MASK2 $ARG_SACEM_OFF1 $ARG_SACEM_OFF2 $ARG_FSFB_MASK1 $ARG_FSFB_MASK2 $ARG_FSFB_OFF1 $ARG_FSFB_OFF2 $ARG_ER_MASK1 $ARG_ER_MASK2 $ARG_CODE_CHK_LOCAL $ARG_CODE_CHK_PRTNR $ARG_FILE_SIPC_TX_BASE $ARG_FILE_SIPC_RX_BASE $ARG_FILE_SHM_TX_BASE $ARG_FILE_SHM_RX_BASE $ARG_CTX_SIPC_TX_BASE $ARG_CTX_SIPC_RX_BASE $ARG_CTX_SHM_TX_BASE $ARG_CTX_SHM_RX_BASE $ARG_LOG_SIPC_TX_BASE $ARG_LOG_SHM_TX_BASE $ARG_MAINT_SIPC_TX_BASE $ARG_MAINT_SHM_TX_BASE $ARG_SW_SIGN_LCL $ARG_GW_IP_ADDR $ARG_MULTICASE_IP_ADDR $ARG_LCL_IP_ADDR $ARG_NTW_BASE_PRT $ARG_TIME_Boundary > /MooNSimu/LDS/Logs/mooncoreLogs 2>&1  (wd: /home/admin/LDS_BSL5.5)
        self._client.close()


    def StopRBCOnHost(self):
        self.log('Stopping the MooN Simulator of ' + self._RBCName)
        self._client.connect(self._RBCip, port=self._RBCport,  username=self._RBCuser, password=self._RBCpass)
        cmds = f'sudo rm -f /MooNSimu/LDS/Config/sipc_ntw_0_to_4'
        self.sendCmd(cmds)

        cmds = f'sudo rm -f /MooNSimu/LDS/Executables/*'
        self.sendCmd(cmds)

        self.log('start remove config')
        cmds = f'sudo rm -f /MooNSimu/LDS/Config/*'
        self.sendCmd(cmds)
        self.log('stop remove config')

        cmds = f'/home/admin/LDS_BSL5.5/stop_moon_simu.sh'
        self.sendCmd(cmds)

        self._client.close()


    def GetLogs(self):
        self.log('Get logs of ' + self._RBCName)
        # TODO: remove file in Logs/
        self._client.connect(self._RBCip, port=self._RBCport,  username=self._RBCuser, password=self._RBCpass)
        scp = SCPClient(self._client.get_transport())

        try:
            scp.get('/MooNSimu/LDS/Logs/', './', recursive=True)
            scp.get('/var/log/syslog', 'Logs/')
            scp.get('/MooNSimu/LDS/Executables/moon.err', 'Logs/')
            scp.get('/MooNSimu/LDS/Executables/moon1.log', 'Logs/')
        except Exception as inst:
            self.log(inst)

        try:
            scp.get('/var/lib/lxc/mgapp/home/imp1.log', 'Logs/')
            scp.get('/var/lib/lxc/mgapp/home/imp2.log', 'Logs/')
        except Exception as inst:
            self.log(inst)
        self._client.close()


    def StopVM(self):

        self.log('Stopping the VM of ' + self._RBCName)
        self._client.connect(self._RBCip, port=self._RBCport,  username=self._RBCuser, password=self._RBCpass)

        cmds = f'sudo rm /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)

        cmds = f'sudo rm -rf /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)

        cmds = f'sudo ls /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)

        #useless:

        #result = subprocess.run(['VBoxManage', 'controlvm', self._RBCName, 'acpipowerbutton'], shell=True, cwd=VBoxPath, capture_output=True, text=True)
        #self.log("stdout:" + result.stdout)
        #self.log("stderr:" + result.stderr)

        result = subprocess.run(['VBoxManage', 'controlvm', self._RBCName, 'poweroff'],
                                shell=True, cwd=VBoxPath, capture_output=True, text=True)
        self.log("stdout:" + result.stdout)
        self.log("stderr:" + result.stderr)

        self._client.close()


    def StartVM(self):
        
        InterfaceName1 = "VirtualBox Host-Only Ethernet Adapter #2"
        InterfaceName2 = "intnet"
        InterfaceName3 = "VirtualBox Host-Only Ethernet Adapter #3"

        #p = subprocess.run(['VBoxManage' , '-v'] , shell=True, cwd=VBoxPath)
        result = subprocess.run(['VBoxManage', 'modifyvm', self._RBCName, '--nic2', 'hostonly',
                                '--hostonlyadapter2', InterfaceName1], shell=True, cwd=VBoxPath, capture_output=True, text=True)
        self.log("stdout:" + result.stdout)
        self.log("stderr:" + result.stderr)

        result = subprocess.run(['VBoxManage', 'modifyvm', self._RBCName, '--nic3', 'intnet', '--intnet2',
                                InterfaceName2], shell=True, cwd=VBoxPath, capture_output=True, text=True)
        self.log("stdout:" + result.stdout)
        self.log("stderr:" + result.stderr)

        result = subprocess.run(['VBoxManage', 'modifyvm', self._RBCName, '--nic4', 'hostonly',
                                '--hostonlyadapter4', InterfaceName3], shell=True, cwd=VBoxPath, capture_output=True, text=True)
        self.log("stdout:" + result.stdout)
        self.log("stderr:" + result.stderr)

        result = subprocess.run(['VBoxManage', 'startvm', self._RBCName, '--type',
                                 'headless'], shell=True, cwd=VBoxPath, capture_output=True, text=True)
        self.log("stdout:" + result.stdout)
        self.log("stderr:" + result.stderr)

        #os.chdir(VBoxPath)

        #print("Current working directory: {0}".format(os.getcwd()))

        #response = os.system('VBoxManage.exe --nologo startvm '+ self._RBCName +'') # --type headless

        #result = subprocess.run(['rmdir', '/Q', '/S', 'C:\\Users\\alstom\\.ssh'], shell=True, capture_output=True, text=True)
        #self.log("stdout:" + result.stdout)
        #self.log("stderr:" + result.stderr)

        self.log('LDS Simulator ' + self._RBCName + ' is booting up ...')

        #time.sleep(2)

        #ping until the vm answer
        retry = 0
        while retry < num_retries:
            response = os.system("ping -n 1 " + self._RBCip + " -S " + Hostvmadapteraddr) #ping with specific source adapter to avoid default gateway
            if response == 0:
                retry = num_retries                
            else:
                retry += 1
                time.sleep(2)
            
        time.sleep(2)
        
        retry = 0
        while retry < num_retries:
            socket.setdefaulttimeout(10)
            timeout = socket.getdefaulttimeout
            #print(timeout)
            localclient = (Hostvmadapteraddr, 0)
            remoteServ = (self._RBCip, 22)
            try:
                mysocket = socket.create_connection(address=remoteServ, source_address=localclient)

                data = mysocket.recv(1024)
                sdata = data.decode("utf-8")

                print(sdata)
                if sdata.find('SSH', 0, len(sdata)) != -1:
                    retry = num_retries 
                else:
                    retry += 1
                    time.sleep(2)
            
            except socket.error:
                self.log(str(socket.error))
                retry += 1
                time.sleep(2)

        retry = 0
        while retry < num_retries:
            try:
                self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self._client.connect(self._RBCip, port=self._RBCport,  username=self._RBCuser, password=self._RBCpass,  timeout=5)
                scp = SCPClient(self._client.get_transport())
                retry = num_retries
            except socket.error:
                self.log(str(socket.error))
                self._client.close()
                time.sleep(5)
                retry += 1

        cmds = f'sudo rm -rf /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)

        # TODO: test if stdout containg: sudo: no tty present and no askpass program specified

        cmds = f'sudo mkdir /MooNSimu'
        self.sendCmd(cmds)
        cmds = f'sudo mount /dev/sdb1 /MooNSimu'
        self.sendCmd(cmds)
        cmds = f'sudo rm -rf /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)
        cmds = f'sudo mkdir /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)
        cmds = f'sudo mount /dev/sdb1 /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)
        cmds = f'sudo mkdir /MooNSimu/LDS'
        self.sendCmd(cmds)
        cmds = f'sudo mkdir /home/admin/LDS_BSL5.5/scripts'
        self.sendCmd(cmds)
        cmds = f'sudo mkdir /etc/default/alchemist_lib'
        self.sendCmd(cmds)
        cmds = f'sudo mkdir /etc/default/alchemist_lib'
        self.sendCmd(cmds)
        cmds = f'sudo chmod -R 777 /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)
        cmds = f'sudo chmod -R 777 /MooNSimu'
        self.sendCmd(cmds)
        cmds = f'sudo chmod -R 777 /home/admin/LDS_BSL5.5/scripts'
        self.sendCmd(cmds)
        cmds = f'sudo chmod -R 777 /etc/default/alchemist_lib'
        self.sendCmd(cmds)
        cmds = f'sudo chmod -R 777 /etc/default/logger_lib'
        self.sendCmd(cmds)

        scp.put(self._workingDir + 'MooN_Simu_Runtime.tar.gz', recursive=True, remote_path='/home/admin/LDS_BSL5.5')

        time.sleep(2)
        self.log('Files are copied into LDS Simulator ' + self._RBCName)

        cmds = f'sudo chmod -R 777 /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)
        cmds = f'tar -zxf /home/admin/LDS_BSL5.5/MooN_Simu_Runtime.tar.gz -C /home/admin/LDS_BSL5.5/'
        self.sendCmd(cmds)
        cmds = f'rm /home/admin/LDS_BSL5.5/MooN_Simu_Runtime.tar.gz'
        self.sendCmd(cmds)
        cmds = f'sudo chmod -R 777 /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)
        cmds = f'/home/admin/LDS_BSL5.5/MooN_Simu_Runtime.sh'
        self.sendCmd(cmds)

        cmds = f'sudo cp /home/admin/LDS_BSL5.5/bootmisc.sh /etc/init.d/'
        self.sendCmd(cmds)
        cmds = f'sudo cp /home/admin/LDS_BSL5.5/save-rtc.sh /etc/init.d/'
        self.sendCmd(cmds)
        cmds = f'sudo cp /home/admin/LDS_BSL5.5/moonux.mgapp /etc/init.d/'
        self.sendCmd(cmds)
        cmds = f'sudo mkdir -p /var/lib/lxc/mgapp/rfs'
        self.sendCmd(cmds)
        cmds = f'sudo tar -zxf /MooNSimu/rootfs.tar.gz -C /var/lib/lxc/mgapp/rfs/'
        self.sendCmd(cmds)
        cmds = f'sudo tar -zxf /MooNSimu/gwguestapp.tar.gz -C /'
        self.sendCmd(cmds)
        cmds = f'sudo tar -zxf /MooNSimu/mgapp.tar.gz -C /var/lib/lxc/mgapp'
        self.sendCmd(cmds)
        cmds = f'sudo cp -rf /var/lib/lxc/mgapp/etc /var/lib/lxc/mgapp/rfs/'
        self.sendCmd(cmds)
        cmds = f'sudo cp -rf /MooNSimu/LDS/Gid/ /home/admin/LDS_BSL5.5/'
        self.sendCmd(cmds)

        cmds = f'sudo chmod -R 777 /home/admin/LDS_BSL5.5'
        self.sendCmd(cmds)
        cmds = f'sudo chmod 777 /etc/init.d/moonux.mgapp'
        self.sendCmd(cmds)

        try:
            scp.get('/MooNSimu/LDS/Gid/SCU.gid', '.')
            scp.get('/home/admin/LDS_BSL5.5/MooN_Simu.conf', '.')
        except Exception as inst:
            self.log(inst)

        cmds = f'sudo mkdir /mnt/persist/Cyber'
        self.sendCmd(cmds)
        cmds = f'sudo mkdir /mnt/persist/Cyber/certs'
        self.sendCmd(cmds)
        cmds = f'sudo chmod -R 777 /mnt/persist/Cyber'
        self.sendCmd(cmds)

        cmds = f'sudo ln -s /home/admin/LDS_BSL5.5/ /LDS_BSL5.5'
        self.sendCmd(cmds)

        self.log('Symbolic link created for ' + self._RBCName)

        # warning pscp -v ???
        scp.put(self._workingDir + 'start_moon_simu.sh', recursive=True, remote_path='/LDS_BSL5.5/')
        # warning pscp -v ???
        scp.put(self._workingDir + 'stop_moon_simu.sh', recursive=True, remote_path='/LDS_BSL5.5/')

        cmds = f'sudo chmod -R 777 /var/lib/lxc/mgapp/rfs/etc/init.d/runguestapp.sh'
        self.sendCmd(cmds)

        # warning pscp -v ???
        scp.put(self._workingDir + 'runguestapp.sh', recursive=True, remote_path='/var/lib/lxc/mgapp/rfs/etc/init.d')

        self._client.close()


    def TestConnectionStatus(self):

        self._client.connect(self._RBCip, port=self._RBCport,  username=self._RBCuser, password=self._RBCpass)
        cmds = f'netstat -tn'
        self.sendCmd(cmds)

        cmds = f'netstat -au'
        self.sendCmd(cmds)

        self._client.close()

    def ping(self):
        response = os.system("ping -n 1 " + self._RBCip)
        if response == 0:
            return True
        else:
            return False

if __name__ == "__main__":

    count = len(sys.argv)
    if count <= 1: 
        print('incorrect number of parameters')

    action = sys.argv[1]
    if action == "start" and count == 6:
        aRbcMgr = RBCUtils(workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], RBCip=sys.argv[5])
        aRbcMgr.StartVM()
        time.sleep(2)
        aRbcMgr.StartRBCOnHost()
        # workingDir, RBCVersion, RBCName,  RBCip
        #C:/Users/anborrem/AppData/Local/Programs/Python/Python39-32/python.exe c:/gitrepo/RadioBlockCenterTestEnv/RBCUtils.py start "C:\\ETCS2-TRK_TestEnv_93B\\Simu\\MooN_Simu\\RBC5\\" RBC_MooN_93000 RBC5_93B 192.168.56.55 

    if action == "start" and count == 8:
        aRbcMgr = RBCUtils(workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], RBCip=sys.argv[5], RBCuser=sys.argv[6], RBCpass=sys.argv[7])
        aRbcMgr.StartVM()
        time.sleep(2)
        aRbcMgr.StartRBCOnHost()
        # workingDir, RBCVersion, RBCName,  RBCip
        #C:/Users/anborrem/AppData/Local/Programs/Python/Python39-32/python.exe c:/gitrepo/RadioBlockCenterTestEnv/RBCUtils.py start "C:\\ETCS2-TRK_TestEnv_93B\\Simu\\MooN_Simu\\RBC5\\" RBC_MooN_93000 RBC5_93B 192.168.56.55 


    if action == "stop" and count == 6:
        aRbcMgr = RBCUtils(workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], RBCip=sys.argv[5])
        aRbcMgr.StopRBCOnHost()
        time.sleep(2)
        aRbcMgr.StopVM()

    if action == "help":
        print('start workingDir RBCVersion RBCName  RBCip')
        print('C:/Users/anborrem/AppData/Local/Programs/Python/Python39-32/python.exe c:/gitrepo/RadioBlockCenterTestEnv/RBCUtils.py start "C:\\ETCS2-TRK_TestEnv_93B\\Simu\\MooN_Simu\\RBC5\\" RBC_MooN_93000 RBC5_93B 192.168.56.55')
        print('C:/Users/anborrem/AppData/Local/Programs/Python/Python39-32/python.exe c:/gitrepo/RadioBlockCenterTestEnv/RBCUtils.py start "C:\\ETCS2-TRK_TestEnv_93B\\Simu\\MooN_Simu\\RBC5\\" RBC_MooN_93000 IMP_Gateway_93A 192.168.56.3 imp_gateway impgateway')


