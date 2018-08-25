#!/usr/bin/python
# socket code adapted from Richard Garsthagen's scripts at pi3dscan.com
# NOTE: look into python socketserver module or tornado library to handle sockets
# 12/19/16

import socket
import struct
import subprocess
import time
import datetime
import picamera

pixels = (2592, 1944)
framerate = 1
led = False
vflip = True
hflip = True
meter_mode = 'backlit'
iso = 100


def config_socket():
    MCAST_GRP = '225.1.1.1'
    MCAST_PORT = 3179

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # '' is a symbolic name for host parameter that means all available interfaces
    sock.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return sock

debug = 1  # Turn debug message on/off


if __name__ == '__main__':
    sock = config_socket()

    while True:
        print("listening...")
        data = sock.recv(10240).decode()
        rdata = data[1:]
        rcmd = ord(data[0])

        if debug == 1:
            print("Received cmd: {}".format(str(rcmd)))
            print("Data: {}".format(rdata))

        if rcmd == 1 and rdata:
            print("shooting still @ {}".format(datetime.datetime.now().strftime("%H:%M:%S")))
            cmd = "raspistill " + rdata
            pid = subprocess.call(cmd, shell=True)
            print("done shooting still @ {}\n".format(datetime.datetime.now().strftime("%H:%M:%S")))

        elif rcmd == 1:
            with picamera.PiCamera(resolution=pixels, framerate=framerate) as picam:
                picam.iso = iso
                picam.led = led
                picam.vflip = vflip
                picam.hflip = hflip
                picam.meter_mode = meter_mode

                print("calibrating picam instance")
                time.sleep(5)

                print("shooting still @ {}".format(datetime.datetime.now().strftime("%H:%M:%S")))
                picam.capture('/home/pi/tests/socket_pics/test02-{}.jpg'.format(socket.gethostname()))
                print("done shooting still @ {}\n".format(datetime.datetime.now().strftime("%H:%M:%S")))
