from scapy.all import Ether, ARP, RARP, srp,sr1, ICMP, IP
import time

def RARP(mac,timeout=2) :
    """
Make RARP request
\nmac : MAC adresse to retrieve IP
\nTimeout : timeout of the request. Default is 2
\nReturn : List of tupple of each result
    """
    returnlist=[]
    rarp_request = RARP(op=1, hwsrc=mac)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    rarp_request_broadcast = broadcast / rarp_request
    answered_list = srp(rarp_request_broadcast, timeout=timeout, verbose=False)[0]
    for element in answered_list:
        returnlist.append((element[1].hwsrc,element[1].psrc))
    return returnlist

def ARP(ip_address,timeout=2):
    """
Make ARP request
\nip_address : IP adresse to retrieve MAC
\nTimeout : timeout of the request. Default is 2
\nReturn : List of tupple of each result
    """
    returnlist=[]
    arp_request = ARP(pdst=ip_address)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_packet = ether / arp_request
    result = srp(arp_request_packet, timeout=timeout, verbose=False)[0]
    if result:
        for sent, received in result:
            returnlist.append((received.psrc,received.hwsrc))
            return returnlist
    else:
        return None

def Ping(host,timeout=2):
    """
\nPing host
\n-host : host to ping
\n-timeout : request timeout. Default value is 2 
\nReturn : latency in milliseconds
    """
    packet = IP(dst=host) / ICMP()
    start_time = time.time()
    response = sr1(packet, timeout=timeout, verbose=False)
    end_time = time.time()

    if response is None:
        return None
    else:
        latency = (end_time - start_time) * 1000
        return latency
