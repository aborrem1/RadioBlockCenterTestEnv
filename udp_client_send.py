import socket
import struct
import time
import xmlrpc.client
import sys
UDP_IP = "127.0.0.1"
UDP_PORT = 7040

def getXML(params, method):
    # params = ({"tracks": ['track1', 'track2', 'track3']}, )
    return xmlrpc.client.dumps(params, methodname=method, methodresponse=None, encoding=None, allow_none=True)

def SendDataToUDP(data, portnum, help):
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    print("---------------------------------------------------------")
    # sock.connect((UDP_IP, UDP_PORT))
    ttl = struct.pack('b', 32)  #// 32 
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    # sock.send(bytes(data.encode('ascii')))
    sock.sendto(bytes(data.encode('ascii')), ('127.0.0.1', portnum))
    sock.close()
    print("Data sent for", help)


p = ({'trainId': '1001', 'trainLength': 8000, 'head': 'RIGHT', 'antennaPosition': 0, 'direction': 'LEFT_RIGHT'},)
xml = getXML(p, 'TRAINMANAGEMENT.trainInfo')
SendDataToUDP(xml, 7040, "TrainInfo")
time.sleep(1)

p = ({'trainId': 1001, 'position': 0.0, 'speed': 0.0},)
xml = getXML(p, 'TRAINMANAGEMENT.posReport')
SendDataToUDP(xml, 7040, 'TRAINMANAGEMENT.posReport')
time.sleep(1)

p = ({'trainID': 1001, 'nidEngine': '12345', 'frame': 'MDEyMzQ1Njc4OUFCQw==', 'frameLength': 13},)
xml = getXML(p, 'RBCMESSAGE.Report')
SendDataToUDP(xml, 7040, "RBCMESSAGE.Report")
time.sleep(1)


p = ({'application': 'TEST', 'time': 0.0, 'callId': 'TEST.GET_TRAIN_LIST.1', 'method': 'GET_TRAIN_LIST', 'parameters': {'TimeOut': 10}},)
xml = getXML(p, 'AUTOMATION.execute')
SendDataToUDP(xml, 7010, 'AUTOMATION.execute')
time.sleep(1)



# old
"""

#port 7040
data_ = r'<?xml version="1.0"?><methodCall><methodName>TRAINMANAGEMENT.posReport</methodName><params><param><value><struct><member><name>trainId</name><value><int>1001</int></value></member><member><name>position</name><value><double>126247</double></value></member><member><name>speed</name><value><double>200</double></value></member></struct></value></param></params></methodCall>'

data_traininfo = r'<?xml version="1.0"?><methodCall><methodName>TRAINMANAGEMENT.trainInfo</methodName><params><param><value><struct><member><name>trainId</name><value><string>1001</string></value></member><member><name>trainLength</name><value><int>8000</int></value></member><member><name>head</name><value><string>RIGHT</string></value></member><member><name>antennaPosition</name><value><int>0</int></value></member><member><name>direction</name><value><string>LEFT_RIGHT</string></value></member></struct></value></param></params></methodCall>'


data_trainposreport = r'<?xml version="1.0"?><methodCall><methodName>TRAINMANAGEMENT.posReport</methodName><params><param><value><struct><member><name>trainId</name><value><int>1001</int></value></member><member><name>position</name><value><double>0</double></value></member><member><name>speed</name><value><double>0</double></value></member></struct></value></param></params></methodCall>'

data_RBCreport=r'<?xml version="1.0"?><methodCall><methodName>RBCMESSAGE.Report</methodName><params><param><value><struct><member><name>trainID</name><value><int>1001</int></value></member><member><name>nidEngine</name><value><string>12345</string></value></member><member><name>frame</name><value><string>MDEyMzQ1Njc4OUFCQw==</string></value></member><member><name>frameLength</name><value><int>13</int></value></member></struct></value></param></params></methodCall>'


#port 7010
data_automatexec = r'<?xml version="1.0"?><methodCall><methodName>AUTOMATION.execute</methodName><params><param><value><struct><member><name>application</name><value><string>TEST</string></value></member><member><name>time</name><value><double>0</double></value></member><member><name>callId</name><value><string>TEST.GET_TRAIN_LIST.1</string></value></member><member><name>method</name><value><string>GET_TRAIN_LIST</string></value></member><member><name>parameters</name><value><struct><member><name>TimeOut</name><value><int>10</int></value></member></struct></value></member></struct></value></param></params></methodCall>'


HWB_CONFIG_data = r'<?xml version="1.0"?><methodCall><methodName>CONFIG.data</methodName><params><param><value><struct><member><name>adaptorConfigData</name><value><string>adaptorConfigData Content</string></value></member></struct></value></param></params></methodCall>'

HWB_CONFIG_tracks = r'<?xml version="1.0"?><methodCall><methodName>CONFIG.tracks</methodName><params><param><value><struct><member><name>tracks</name><value><array><data><value><string>track1</string></value><value><string>track2</string></value><value><string>track3</string></value></data></array></value></member></struct></value></param></params></methodCall>'

"
"""