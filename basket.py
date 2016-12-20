#!/usr/bin/python
# socket code adapted from Richard Garsthagen's scripts at pi3dscan.com
# 12/19/16

import socket
import sys


MCAST_GRP = '225.1.1.1'
MCAST_PORT = 3179


def config_socket():
    dev = "eth0" + "\0"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, dev.encode())
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    return sock


def get_options():
    options = ""
    SCMD = chr(1)  # Command 1 = Shoot photo

    for a in range(1, len(sys.argv)):
        options = options + " " + sys.argv[a]
    SCMD = SCMD + options
    send = SCMD.encode()

    return send


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("please provide raspistill command options")

    else:
        print("Sending shooting command...")

        sock = config_socket()
        send = get_options()

        sock.sendto(send, (MCAST_GRP, MCAST_PORT))
        sock.close()
