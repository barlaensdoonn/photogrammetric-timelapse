#!/usr/bin/python
# socket code adapted from Richard Garsthagen's scripts at pi3dscan.com
# 12/19/16

import socket


MCAST_GRP = '225.1.1.1'
MCAST_PORT = 3179

print("Sending shooting command...")

dev = "eth0" + "\0"
SCMD = chr(1)  # Command 1 = Shoot photo
SCMD = SCMD + " " + "-o" + " " + "test.jpg"
SEND = SCMD.encode()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, dev.encode())
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
sock.sendto(SEND, (MCAST_GRP, MCAST_PORT))
sock.close()
