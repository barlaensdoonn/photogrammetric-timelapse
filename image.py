#!/usr/bin/python
# camera module for photogrammetric timelapse
# 8/30/17

import os
import logging
import datetime
import picamera


class Camera(object):
    '''class to hold camera and file management functions'''

    def __init__(self):
        self.base_pi_path = base_pi_path
        self.base_remote_path = longpaths.base_remote_path
        self.remote_copy_path = '/Volumes/RAGU/longlapse/dayze'
        self.host = longpaths.host
        self.scp_host = longpaths.scp_host
        self.copied = False
        self.pixels = (2592, 1944)
        self.framerate = 1
        self.led = False
        self.vflip = True
        self.hflip = True
        self.meter_mode = 'backlit'
        self.iso = 100
        self.awb_mode = 'off'
        self.awb_gains = (Fraction(447, 256), Fraction(255, 256))
        # self.exposure_mode = 'off'  # exposure_mode off disables picam.analog_gain & picam.digital_gain, which are not directly settable; however picamera docs turning this off after gains have settled
