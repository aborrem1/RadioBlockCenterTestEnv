from RBCUtils import RBCUtils
import time
import threading
import os

matchstring = 'tcp        0      0 175.175.175.200:15500   175.175.175.132:15501   ESTABLISHED'


Rbc5Mgr = RBCUtils(workingDir="C:/ETCS2-TRK_TestEnv_93B/", RBCVersion="RBC_MooN_93000", RBCName="RBC5", VMName="RBC5_93B", RBCip="192.168.56.55")

def startRBC5():
    Rbc5Mgr = RBCUtils(workingDir="C:/ETCS2-TRK_TestEnv_93B/", RBCVersion="RBC_MooN_93000", RBCName="RBC5", VMName="RBC5_93B", RBCip="192.168.56.55")

    Rbc5Mgr.StartVM()
    time.sleep(2)
    Rbc5Mgr.StartRBCOnHost()

def stopRBC5():
    Rbc5Mgr = RBCUtils(workingDir="C:/ETCS2-TRK_TestEnv_93B/", RBCVersion="RBC_MooN_93000", RBCName="RBC5", VMName="RBC5_93B", RBCip="192.168.56.55")

    Rbc5Mgr.StopRBCOnHost()
    time.sleep(2)
    Rbc5Mgr.StopVM()

def getStatus():
    return Rbc5Mgr.TestConnectionStatus()
    

    

if __name__ == "__main__":
    
    s = time.perf_counter()

    OkCount = 0

    for i in range(1):
        startRBC5()
        time.sleep(10)
        result = getStatus()
        if matchstring in result:
            OkCount = OkCount + 1
        stopRBC5()

    print('run ok=' + str(OkCount))

    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")