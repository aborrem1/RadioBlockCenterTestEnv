from RBCUtils import RBCUtils
import time
import threading
import os

import logging #split in flow

#C:/Users/anborrem/AppData/Local/Programs/Python/Python39-32/python.exe c:/gitrepo/RadioBlockCenterTestEnv/startRBC.py start "C:\\ETCS2-TRK_TestEnv_93B\\Simu\\MooN_Simu\\RBC5\\" RBC_MooN_93000 RBC5_93B 192.168.56.55 

def stopRBC5():
    Rbc5Mgr = RBCUtils(workingDir="C:/ETCS2-TRK_TestEnv_93B/", RBCVersion="RBC_MooN_93000", RBCName="RBC5", VMName="RBC5_93B", RBCip="192.168.56.55")

    Rbc5Mgr.StopRBCOnHost()
    time.sleep(2)
    Rbc5Mgr.StopVM()

def stopRBC6():
    Rbc6Mgr = RBCUtils(workingDir="C:/ETCS2-TRK_TestEnv_93B/", RBCVersion="RBC_MooN_93000", RBCName="RBC6", VMName="RBC6_93B", RBCip="192.168.56.56")

    Rbc6Mgr.StopRBCOnHost()
    time.sleep(2)
    Rbc6Mgr.StopVM()   


if __name__ == "__main__":
    
    s = time.perf_counter()

    os.chdir('c:\\')

        # Print the current working directory
    print("Current working directory: {0}".format(os.getcwd()))

    threads = list()
    x = threading.Thread(target=stopRBC5)
    threads.append(x)
    x.start()

    y = threading.Thread(target=stopRBC6)
    threads.append(y)
    y.start()

    for index, thread in enumerate(threads):
        print("Main    : before joining thread %d.", index)
        thread.join()
        print("Main    : thread %d done", index)

    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")