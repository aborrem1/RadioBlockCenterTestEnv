import re
import paramiko
from datetime import datetime
from paramiko import SSHClient
import shutil
import socket
import sys
import os
import subprocess
import time

from scp import SCPClient
import FilesUtils


DefaultPort = 22
Defaultuser = 'admin'
Defaultpassword = 'admin'
Hostvmadapteraddr = '192.168.56.101' 
VBoxPath = 'C:/Program Files/Oracle/VirtualBox/'

InterfaceName1 = "VirtualBox Host-Only Ethernet Adapter #2"
InterfaceName2 = "intnet"
InterfaceName3 = "VirtualBox Host-Only Ethernet Adapter #3"

num_retries = 10


timeformat = "%Y%m%d_%H%M%S.%f: "


class RBCUtils:

    def __init__(self, workingDir, RBCVersion, RBCName, VMName,  RBCip, RBCport=DefaultPort, RBCuser=Defaultuser, RBCpass=Defaultpassword):
        self._client = SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._originWorkingDir = workingDir
        self._workingDir = workingDir + 'Simu/MooN_Simu/' + RBCName + '/'
        self._RBCVersion = RBCVersion
        self._RBCName = RBCName
        self._VMName = VMName
        self._RBCip = RBCip
        self._RBCport = RBCport
        self._RBCuser = RBCuser
        self._RBCpass = RBCpass

    def runCmd(self, cmds, workingdir=VBoxPath):

        result = subprocess.run(
            cmds, shell=True, cwd=workingdir, capture_output=True, text=True)

        if (result.stdout != ''):
            self.log("stdout:" + result.stdout)
        if (result.stderr != ''):
            self.log("stderr:" + result.stderr)
        return result

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

        result = stdout, stderr
        return result

        # if stderr.channel.recv_exit_status() != 0:
        #     print("The following error occured:" + str(stderr.readlines()))
        # print(stdout.readlines())

    def log(self, message):
        now = datetime.now()
        print(now.strftime(timeformat) + str(message))

    def StartRBCOnHost(self):

        self._client.connect(self._RBCip, port=self._RBCport,
                             username=self._RBCuser, password=self._RBCpass)
        try:
            scp = SCPClient(self._client.get_transport())

            cmds = 'sudo chmod -R 777 /MooNSimu/LDS/Executables'
            self.sendCmd(cmds)

            scp.put(self._workingDir + "Config", recursive=True,
                remote_path='/MooNSimu/LDS')  # "./Config"

            #print(self._workingDir + "Config\\")

            scp.put(self._workingDir + 'Executables', recursive=True,
                remote_path='/MooNSimu/LDS')  # './Executables'
            scp.put(self._workingDir + 'MooN_Simu.conf', recursive=True,
                remote_path='/home/admin/LDS_BSL5.5')
            #scp.put('check.sh', recursive=True, remote_path='/home/admin/LDS_BSL5.5/')
            scp.put(self._workingDir + 'SCU.gid', recursive=True,
                remote_path='/home/admin/LDS_BSL5.5/Gid/')

            cmds = 'sudo chmod -R 777 /MooNSimu/LDS/Executables'
            self.sendCmd(cmds)

            cmds = 'sudo chmod -R 777 /MooNSimu/LDS/Config'
            self.sendCmd(cmds)

            cmds = 'sudo chmod -R 777 /home/admin/LDS_BSL5.5/*'
            self.sendCmd(cmds)

            self.log("Starting the MooN Simulator of " + self._RBCName)

            cmds = '/home/admin/LDS_BSL5.5/start_moon_simu.sh'
            result = self.sendCmd(cmds)

            # TODO: check if return if different of:
            # /home/admin/LDS_BSL5.5/start_moon_simu.sh: line 283:  1639 Aborted                 
            # (core dumped) /MooNSimu/LDS/Executables/mooncore-cb 
            # $ARG_CH $ARG_NVRAM $ARG_SACEM_MASK1 $ARG_SACEM_MASK2 $ARG_SACEM_OFF1 $ARG_SACEM_OFF2 $ARG_FSFB_MASK1 $ARG_FSFB_MASK2 
            # $ARG_FSFB_OFF1 $ARG_FSFB_OFF2 $ARG_ER_MASK1 $ARG_ER_MASK2 $ARG_CODE_CHK_LOCAL $ARG_CODE_CHK_PRTNR $ARG_FILE_SIPC_TX_BASE 
            # $ARG_FILE_SIPC_RX_BASE $ARG_FILE_SHM_TX_BASE $ARG_FILE_SHM_RX_BASE $ARG_CTX_SIPC_TX_BASE $ARG_CTX_SIPC_RX_BASE 
            # $ARG_CTX_SHM_TX_BASE $ARG_CTX_SHM_RX_BASE $ARG_LOG_SIPC_TX_BASE $ARG_LOG_SHM_TX_BASE $ARG_MAINT_SIPC_TX_BASE 
            # $ARG_MAINT_SHM_TX_BASE $ARG_SW_SIGN_LCL $ARG_GW_IP_ADDR $ARG_MULTICASE_IP_ADDR $ARG_LCL_IP_ADDR $ARG_NTW_BASE_PRT 
            # $ARG_TIME_Boundary > /MooNSimu/LDS/Logs/mooncoreLogs 2>&1  (wd: /home/admin/LDS_BSL5.5)
        finally:
            self._client.close()

    def StopRBCOnHost(self):
        self.log('Stopping the MooN Simulator of ' + self._RBCName)
        self._client.connect(self._RBCip, port=self._RBCport,
                             username=self._RBCuser, password=self._RBCpass)
        try:
            cmds = 'sudo rm -f /MooNSimu/LDS/Config/sipc_ntw_0_to_4'
            self.sendCmd(cmds)

            cmds = 'sudo rm -rf /MooNSimu/LDS/Executables/*'
            self.sendCmd(cmds)

            #self.log('start remove config')
            cmds = 'sudo rm -f /MooNSimu/LDS/Config/*'
            self.sendCmd(cmds)
            #self.log('stop remove config')

            cmds = '/home/admin/LDS_BSL5.5/stop_moon_simu.sh'
            self.sendCmd(cmds)
        finally:
            self._client.close()

    def GetLogs(self):
        slogFolder = 'Logs/'
        self.log('Get logs of ' + self._RBCName)
        # TODO: remove file in Logs/

        FilesUtils.removefolder(self._workingDir + slogFolder)

        self._client.connect(self._RBCip, port=self._RBCport,
                             username=self._RBCuser, password=self._RBCpass)

        try:
            scp = SCPClient(self._client.get_transport())

            try:
                scp.get('/MooNSimu/LDS/Logs/', self._workingDir, recursive=True)
            except Exception as inst:
                self.log(inst)

            try:
                scp.get('/var/log/syslog', self._workingDir + slogFolder)
            except Exception as inst:
                self.log(inst)

            try:
                scp.get('/MooNSimu/LDS/Executables/moon.err',
                    self._workingDir + slogFolder)
            except Exception as inst:
                self.log(inst)

            try:
                scp.get('/MooNSimu/LDS/Executables/moon1.log',
                    self._workingDir + slogFolder)
            except Exception as inst:
                self.log(inst)

            try:
                scp.get('/var/lib/lxc/mgapp/home/imp1.log',
                    self._workingDir + slogFolder)
            except Exception as inst:
                self.log(inst)

            try:
                scp.get('/var/lib/lxc/mgapp/home/imp2.log',
                    self._workingDir + slogFolder)
            except Exception as inst:
                self.log(inst)
        finally:
            self._client.close()

    def StopVM(self):

        self.log('Stopping the VM of ' + self._RBCName)
        

        # get running VMS
        result = self.runCmd(['VBoxManage', 'list', 'runningvms'])

        p = re.compile(r'"(.*?)"')
        list = p.findall(result.stdout)

        stopvm = False
        for x in list:
            if x == self._VMName:
                stopvm = True
                # exit???

        if stopvm:
                # acpipowerbutton seems useless
                #result = subprocess.run(['VBoxManage', 'controlvm', self._RBCName, 'acpipowerbutton'], shell=True, cwd=VBoxPath, capture_output=True, text=True)
                #self.log("stdout:" + result.stdout)
                #self.log("stderr:" + result.stderr)
                self._client.connect(self._RBCip, port=self._RBCport,
                             username=self._RBCuser, password=self._RBCpass)
                try:
                    cmds = 'sudo rm /home/admin/LDS_BSL5.5'
                    self.sendCmd(cmds)

                    cmds = 'sudo rm -rf /home/admin/LDS_BSL5.5'
                    self.sendCmd(cmds)

                    cmds = 'sudo ls /home/admin/LDS_BSL5.5'
                    self.sendCmd(cmds)
                finally:
                    self._client.close()

                self.runCmd(['VBoxManage', 'controlvm', self._VMName, 'poweroff'])
        else:
            self.log('VM is already stoped!!!')

    def StartVM(self):
        # get running VMS
        result = self.runCmd(['VBoxManage', 'list', 'runningvms'])

        p = re.compile(r'"(.*?)"')
        list = p.findall(result.stdout)
        startvm = True
        for x in list:
            if x == self._VMName:
                startvm = False
                self.log('VM is already started!!!')
                # exit???

        if startvm:
            self.runCmd(['VBoxManage', 'modifyvm', self._VMName, '--nic2', 'hostonly',
                         '--hostonlyadapter2', InterfaceName1])
            self.runCmd(['VBoxManage', 'modifyvm', self._VMName, '--nic3', 'intnet', '--intnet2',
                         InterfaceName2])
            self.runCmd(['VBoxManage', 'modifyvm', self._VMName, '--nic4', 'hostonly',
                         '--hostonlyadapter4', InterfaceName3])
            self.runCmd(['VBoxManage', 'startvm', self._VMName, '--type',
                         'headless'])

        # response = os.system('VBoxManage.exe --nologo startvm '+ self._VMName +'') # --type headless

        #result = subprocess.run(['rmdir', '/Q', '/S', 'C:\\Users\\alstom\\.ssh'], shell=True, capture_output=True, text=True)
        #self.log("stdout:" + result.stdout)
        #self.log("stderr:" + result.stderr)

        self.log('LDS Simulator ' + self._RBCName + ' is booting up ...')

        # ping until the vm answer
        retry = 0
        while retry < num_retries:
            # ping with specific source adapter to avoid default gateway
            response = os.system(
                "ping -n 1 " + self._RBCip + " -S " + Hostvmadapteraddr)
            if response == 0:
                retry = num_retries
            else:
                retry += 1
                time.sleep(2)

        retry = 0
        while retry < num_retries:
            socket.setdefaulttimeout(10)
            timeout = socket.getdefaulttimeout
            localclient = (Hostvmadapteraddr, 0)
            remoteServ = (self._RBCip, 22)
            try:
                self.log('try to reach port 22')
                mysocket = socket.create_connection(
                    address=remoteServ, source_address=localclient)
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
                self._client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())
                self._client.connect(self._RBCip, port=self._RBCport,
                                     username=self._RBCuser, password=self._RBCpass,  timeout=2)
                scp = SCPClient(self._client.get_transport())
                retry = num_retries
            except socket.error:
                self.log(str(socket.error))
                self._client.close()
                time.sleep(2)
                retry += 1
                if retry == num_retries:
                    self.log(
                        'Leaving the script, please retry to launch it. ' + self._RBCName)
                    sys.exit()
        
        try:
            cmds = 'sudo rm -rf /home/admin/LDS_BSL5.5'
            self.sendCmd(cmds)

            # TODO: test here if stdout containg: 'sudo: no tty present and no askpass program specified'

            cmds = 'sudo mkdir /MooNSimu'  # '/MooNSimu': File exists
            self.sendCmd(cmds)
            cmds = 'sudo mount /dev/sdb1 /MooNSimu'
            self.sendCmd(cmds)

            # TODO: check mount

            cmds = 'sudo rm -rf /home/admin/LDS_BSL5.5'
            self.sendCmd(cmds)
            cmds = 'sudo mkdir /home/admin/LDS_BSL5.5'
            self.sendCmd(cmds)
            cmds = 'sudo mount /dev/sdb1 /home/admin/LDS_BSL5.5'
            self.sendCmd(cmds)

            # TODO: check mount

            cmds = 'sudo mkdir /MooNSimu/LDS'  # '/MooNSimu/LDS': File exists
            self.sendCmd(cmds)
            # '/home/admin/LDS_BSL5.5/scripts': File exists
            cmds = 'sudo mkdir /home/admin/LDS_BSL5.5/scripts'
            self.sendCmd(cmds)
            # '/etc/default/alchemist_lib': File exists
            cmds = 'sudo mkdir /etc/default/alchemist_lib'
            self.sendCmd(cmds)
            cmds = 'sudo mkdir /etc/default/logger_lib'
            self.sendCmd(cmds)

            #self.log('LDS Simulator ' + self._RBCName +
            #     ' set permission directory')
            cmds = 'sudo chmod -R 777 /home/admin/LDS_BSL5.5'
            self.sendCmd(cmds)
            cmds = 'sudo chmod -R 777 /MooNSimu'
            self.sendCmd(cmds)
            cmds = 'sudo chmod -R 777 /home/admin/LDS_BSL5.5/scripts'
            self.sendCmd(cmds)
            cmds = 'sudo chmod -R 777 /etc/default/alchemist_lib'
            self.sendCmd(cmds)
            cmds = 'sudo chmod -R 777 /etc/default/logger_lib'
            self.sendCmd(cmds)
            #self.log('LDS Simulator ' + self._RBCName +
            #     ' set permission directory finish')

            scp.put(self._workingDir + 'MooN_Simu_Runtime.tar.gz',
                recursive=True, remote_path='/home/admin/LDS_BSL5.5')

            #time.sleep()
            #self.log('Files are copied into LDS Simulator ' + self._RBCName)

            cmds = 'sudo chmod -R 777 /home/admin/LDS_BSL5.5'
            self.sendCmd(cmds)
            cmds = 'tar -zxf /home/admin/LDS_BSL5.5/MooN_Simu_Runtime.tar.gz -C /home/admin/LDS_BSL5.5/'
            self.sendCmd(cmds)
            cmds = 'rm /home/admin/LDS_BSL5.5/MooN_Simu_Runtime.tar.gz'
            self.sendCmd(cmds)
            cmds = 'sudo chmod -R 777 /home/admin/LDS_BSL5.5'
            self.sendCmd(cmds)
            cmds = '/home/admin/LDS_BSL5.5/MooN_Simu_Runtime.sh'
            self.sendCmd(cmds)

            cmds = 'sudo cp /home/admin/LDS_BSL5.5/bootmisc.sh /etc/init.d/'
            self.sendCmd(cmds)
            cmds = 'sudo cp /home/admin/LDS_BSL5.5/save-rtc.sh /etc/init.d/'
            self.sendCmd(cmds)
            cmds = 'sudo cp /home/admin/LDS_BSL5.5/moonux.mgapp /etc/init.d/'
            self.sendCmd(cmds)
            cmds = 'sudo mkdir -p /var/lib/lxc/mgapp/rfs'
            self.sendCmd(cmds)
            cmds = 'sudo tar -zxf /MooNSimu/rootfs.tar.gz -C /var/lib/lxc/mgapp/rfs/'
            self.sendCmd(cmds)
            cmds = 'sudo tar -zxf /MooNSimu/gwguestapp.tar.gz -C /'
            self.sendCmd(cmds)
            cmds = 'sudo tar -zxf /MooNSimu/mgapp.tar.gz -C /var/lib/lxc/mgapp'
            self.sendCmd(cmds)
            cmds = 'sudo cp -rf /var/lib/lxc/mgapp/etc /var/lib/lxc/mgapp/rfs/'
            self.sendCmd(cmds)
            cmds = 'sudo cp -rf /MooNSimu/LDS/Gid/ /home/admin/LDS_BSL5.5/'
            self.sendCmd(cmds)

            cmds = 'sudo chmod -R 777 /home/admin/LDS_BSL5.5'
            self.sendCmd(cmds)
            cmds = 'sudo chmod 777 /etc/init.d/moonux.mgapp'
            self.sendCmd(cmds)

            try:
                scp.get('/MooNSimu/LDS/Gid/SCU.gid', self._workingDir)
            except Exception as inst:
                self.log(inst)

            try:
                scp.get('/home/admin/LDS_BSL5.5/MooN_Simu.conf', self._workingDir)
            except Exception as inst:
                self.log(inst)

            cmds = 'sudo mkdir /mnt/persist/Cyber'
            self.sendCmd(cmds)
            cmds = 'sudo mkdir /mnt/persist/Cyber/certs'
            self.sendCmd(cmds)
            cmds = 'sudo chmod -R 777 /mnt/persist/Cyber'
            self.sendCmd(cmds)

            cmds = 'sudo ln -s /home/admin/LDS_BSL5.5/ /LDS_BSL5.5'
            self.sendCmd(cmds)

            self.log('Symbolic link created for ' + self._RBCName)

            # warning pscp -v (verbose) in .bat script
            scp.put(self._workingDir + 'start_moon_simu.sh',
                recursive=True, remote_path='/LDS_BSL5.5/')
            # warning pscp -v (verbose) in .bat script
            scp.put(self._workingDir + 'stop_moon_simu.sh',
                recursive=True, remote_path='/LDS_BSL5.5/')

            cmds = 'sudo chmod -R 777 /var/lib/lxc/mgapp/rfs/etc/init.d/runguestapp.sh'
            self.sendCmd(cmds)

            # warning pscp -v (verbose) in .bat script
            scp.put(self._workingDir + 'runguestapp.sh', recursive=True,
                remote_path='/var/lib/lxc/mgapp/rfs/etc/init.d')
        finally:
            self._client.close()

    def TestConnectionStatus(self):

        self._client.connect(self._RBCip, port=self._RBCport,
                             username=self._RBCuser, password=self._RBCpass)
        try:
            cmds = 'netstat -tn'
            self.sendCmd(cmds)

            cmds = 'netstat -au'
            self.sendCmd(cmds)
        finally:
            self._client.close()

    def ping(self):
        # ping with specific source adapter to avoid default gateway
        response = os.system("ping -n 1 " + self._RBCip +
                             " -S " + Hostvmadapteraddr)
        if response == 0:
            return True
        else:
            return False

    def ChangeConfig(self):
        self.log("Erasing previous binaries and configuration files...")
        print(self._workingDir)

        #self.runCmd(['del', '/F', '/Q', 'Config/*.bin'], self._workingDir)
        configpath =self._workingDir + 'Config/'
        files=os.listdir(configpath)

        for fname in files:
                #print(fname)
            if fname.find('.bin') >= 0:
                os.remove(configpath + fname)
        
        self.log("Copying configuration files...")
        alchemistpath = self._originWorkingDir + 'ObjectUnderTest/'+ self._RBCVersion + '/' + self._RBCName + '/Alchemist/Alchemist_Outputs/Usb/'
        try:
            configpath = alchemistpath + 'B/imp_protocol.txt'
            shutil.copy2(configpath,  self._workingDir + 'Config/')
            configpath = alchemistpath + 'B/imp_server.txt'
            shutil.copy2(configpath,  self._workingDir + 'Config/')

            configpath = alchemistpath + 'B/'
            files=os.listdir(configpath)

            for fname in files:
                #print(fname)
                if fname.find('.bin') >= 0:
                    shutil.copy2(configpath + fname,  self._workingDir + 'Config/')
            
            configpath = alchemistpath + 'G/'
            files=os.listdir(configpath)

            for fname in files:
                #print(fname)
                if fname.find('.bin') >= 0:
                    shutil.copy2(configpath + fname,  self._workingDir + 'Config/')

            #TODO: TEST_DESIGNER???

        except IOError as e:
            self.log("Unable to copy file. %s" % e)
        except:
            self.log("Unexpected error:", sys.exc_info())

if __name__ == "__main__":

    count = len(sys.argv)
    if count <= 5:
        print('incorrect number of parameters')

    action = sys.argv[1]

    if action == "help":
        print('start workingDir RBCVersion RBCName RBCip')
        print('start workingDir RBCVersion RBCName RBCip vmLogin vmPassword')
        print('stop workingDir RBCVersion RBCName RBCip')
        print('python.exe RBCUtils.py start "C:/ETCS2-TRK_TestEnv_93B/" RBC_MooN_93001 RBC5_93B 192.168.56.55')
        print('python.exe RBCUtils.py start "C:/ETCS2-TRK_TestEnv_93B/" RBC_MooN_93001 IMP_Gateway_93A 192.168.56.3 imp_gateway impgateway')
        print('python.exe RBCUtils.py GetLogs "C:/ETCS2-TRK_TestEnv_93B/" RBC_MooN_93001 RBC5 RBC5_93B 192.168.56.55')
        print('python.exe RBCUtils.py ChangeConfig "C:/ETCS2-TRK_TestEnv_93B/" RBC_MooN_93001 RBC5 RBC5_93B 192.168.56.55')
    if action == "start" and count == 7:
        aRbcMgr = RBCUtils(
            workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], VMName=sys.argv[5], RBCip=sys.argv[6])
        aRbcMgr.StartVM()
        time.sleep(1)
        aRbcMgr.StartRBCOnHost()
        # workingDir, RBCVersion, RBCName,  RBCip
        # C:/Users/anborrem/AppData/Local/Programs/Python/Python39-32/python.exe c:/gitrepo/RadioBlockCenterTestEnv/RBCUtils.py start "C:\\ETCS2-TRK_TestEnv_93B\\Simu\\MooN_Simu\\RBC5\\" RBC_MooN_93000 RBC5_93B 192.168.56.55

    if action == "start" and count == 9:
        aRbcMgr = RBCUtils(workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], VMName=sys.argv[5],
                           RBCip=sys.argv[6], RBCuser=sys.argv[7], RBCpass=sys.argv[8])
        aRbcMgr.StartVM()
        time.sleep(1)
        aRbcMgr.StartRBCOnHost()
        # workingDir, RBCVersion, RBCName,  RBCip
        # C:/Users/anborrem/AppData/Local/Programs/Python/Python39-32/python.exe c:/gitrepo/RadioBlockCenterTestEnv/RBCUtils.py start "C:\\ETCS2-TRK_TestEnv_93B\\Simu\\MooN_Simu\\RBC5\\" RBC_MooN_93000 RBC5_93B 192.168.56.55

    if action == "stopRBC" and count == 7:
        aRbcMgr = RBCUtils(
            workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], VMName=sys.argv[5], RBCip=sys.argv[6])
        aRbcMgr.StopRBCOnHost()

    if action == "stopVM" and count == 7:
        aRbcMgr = RBCUtils(
            workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], VMName=sys.argv[5], RBCip=sys.argv[6])
        aRbcMgr.StopVM()
    
    if action == "stopAll" and count == 7:
        aRbcMgr = RBCUtils(
            workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], VMName=sys.argv[5], RBCip=sys.argv[6])
        aRbcMgr.StopRBCOnHost()
        time.sleep(1)
        aRbcMgr.StopVM()

    if action == "GetLogs" and count == 7:
        aRbcMgr = RBCUtils(
            workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], VMName=sys.argv[5], RBCip=sys.argv[6])
        aRbcMgr.GetLogs()

    if action == "ChangeConfig" and count == 7:
        aRbcMgr = RBCUtils(
            workingDir=sys.argv[2], RBCVersion=sys.argv[3], RBCName=sys.argv[4], VMName=sys.argv[5], RBCip=sys.argv[6])
        aRbcMgr.ChangeConfig()