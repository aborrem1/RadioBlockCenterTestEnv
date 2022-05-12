import socket
import struct
import time
import xmlrpc.client


UDP_IP = '175.175.175.132'
UDP_PORT = 7010
MCAST_GRP = '225.0.0.0' 


def getXML(params, method):
    # params = ({"tracks": ['track1', 'track2', 'track3']}, )
    return xmlrpc.client.dumps(params, methodname=method, methodresponse=None, encoding=None, allow_none=True)

def SendDataToUDP(data, help):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

    mreq = socket.inet_aton(MCAST_GRP) + socket.inet_aton(UDP_IP)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    ttl = struct.pack('b', 1)  #// 32 

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    sock.sendto(data.encode(), (MCAST_GRP, UDP_PORT))

    sock.close()

    print("Data sent for", help)


appName = 'NTG_NOT_SCALABLE'
counter = 1

#p = ({'application': appName, 'time': 0.0, 'callId': appName + '.MUTE_APP.' + str(counter) , 'method': 'MUTE_APP', 'parameters': {'ACTIVATE': False}},)

p = ({'application': appName, 'time': 0.0, 'callId': appName + '.DISCONNECT_EVC.' + str(counter) , 'method': 'DISCONNECT_EVC', 'parameters': {'EVC_ID': 1001}},)

xml = getXML(p, 'AUTOMATION.execute')
SendDataToUDP(xml, 'AUTOMATION.execute')
time.sleep(1)

