#!/usr/bin/python
# socket code adapted from Richard Garsthagen's scripts at pi3dscan.com
# 12/19/16

import socket
import struct
import subprocess


MCAST_GRP = '225.1.1.1'
MCAST_PORT = 3179

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

debug = 1  # Turn debug message on/off

while True:
    data = sock.recv(10240).decode()
    rdata = data[1:]
    rcmd = ord(data[0])
    if debug == 1:
        print("Received cmd: {}".format(str(rcmd)))
        print("Data: {}".format(rdata))
    if (rcmd == 1):
        print("shooting")
        cmd = "raspistill " + rdata
        pid = subprocess.call(cmd, shell=True)
