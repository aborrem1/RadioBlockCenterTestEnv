import os
import socket



def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = ["eth0","eth1","eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break;
            except IOError:
                pass
    return ip


print(os.name)

socket.setdefaulttimeout(10)
timeout = socket.getdefaulttimeout
#print(timeout)
localclient = ("192.168.56.101", 0)
remoteServ = ("192.168.56.55", 22)
remoteServ = ("192.168.56.101", 1235)
mysocket = socket.create_connection(address=remoteServ, source_address=localclient)

#mysocket.sendall(str.encode("hola"))

# Receive the data

while(True):

    data = mysocket.recv(1024)

    

    sdata = data.decode("utf-8")

    print(sdata)
    if sdata.find('SSH', 0, len(sdata)) != -1:
        print('ok')
    else:
        print('nok')
    
    if(data==b''):

        print("Connection closed")

        break

 

mysocket.close()

if os.name != "nt":
    import fcntl
    import struct
    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                # Python 2.7: remove the second argument for the bytes call
            )[20:24])

#print(myip)