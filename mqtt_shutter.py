#!/usr/bin/python3
# process trigger command passed over MQTT
# 8/25/18
# updated 8/31/18

import os
import logging
import subprocess
from time import sleep
from datetime import datetime
from picamera import PiCamera
from fractions import Fraction
import paho.mqtt.client as mqtt
from keys import img_bucket


class SteadyCam:

    def __init__(self, basepath, hostname):
        self.logger = self._init_logger()
        self.cam = self._init_camera()
        self.hostname = hostname
        self.basepath = basepath

    def _init_logger(self):
        logger = logging.getLogger('steady_cam')
        logger.info('mqtt_cam logger instantiated')
        return logger

    def _init_camera(self, resolution=(3280, 2464), shutter_speed=16670, awb_gains=(Fraction(13, 8), Fraction(439, 256))):
        '''
        shutter_speed is set to 16670 to synchronize with the 60hz refresh rate
        of US electricity. this avoids banding in the images.
        the default awb_gains value was queried from a picamera instance exposed
        to 2 daylight balanced bulbs in a studio setting.

        more info:
        https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-consistent-images
        https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-gain
        '''
        cam = PiCamera(resolution=resolution)
        cam.iso = 60
        cam.shutter_speed = 16670  # sync shutter speed with 60hz refresh rate of US electricity to avoid banding
        self.logger.info('warming up camera and setting values...')
        sleep(2)
        cam.exposure_mode = 'off'  # fix the analog and digital gains, which are not directly settable
        cam.awb_mode = 'off'
        cam.awb_gains = awb_gains
        self.logger.info('camera ready')

        return cam

    def _copy_pic(self, pic_path, bucket):
        '''use scp to copy a single image to a remote host'''
        img = pic_path.split('/')[-1]
        status = subprocess.call(['scp', '-p', pic_path, bucket], stdout=subprocess.DEVNULL)

        if status == 0:
            self.logger.info('copied {} to {}'.format(img, bucket))
        else:
            self.logger.error('there was a problem copying {} to {}'.format(img, bucket))

        return status

    def _sync_pics(self, bucket):
        '''
        use rsync to transfer files to a remote host.

        unlike subprocess.run (used in _copy_pic()) which blocks until process
        completes, subprocess.Popen returns immediately
        '''
        self.logger.info('syncing pic to remote machine via rsync')
        return subprocess.Popen(['rsync', '-a', 'imgs/', '--exclude=.gitignore', bucket])

    def snap_pic(self):
        self.logger.debug('time entering snap_pic(): {}'.format(datetime.now()))
        self.logger.info('snapping a pic')
        now = datetime.now()
        pic = os.path.join(self.basepath, 'imgs', '{}_{}.jpg'.format(self.hostname, now.strftime("%Y-%m-%d_%H-%M-%S")))
        self.cam.capture(pic)
        self.logger.debug('time after capture: {}'.format(datetime.now()))
        self.logger.info('snapped a pic')

        return pic

    def transfer_pics(self, pic_path, method='rsync'):
        remote_bucket = os.path.join(img_bucket, self.hostname)
        return self._sync_pics(remote_bucket) if method == 'rsync' else self._copy_pic(pic_path, remote_bucket)

    def delete_pic(self, pic_path):
        self.logger.info('deleting pic: {}'.format(pic_path))
        os.remove(pic_path)

    def close(self):
        '''no one wants memory leaks'''
        self.logger.info('shutting down camera')
        self.cam.close()


class MQTTShutter(mqtt.Client):

    def __init__(self, basepath, hostname, broker='mqtt-broker.local', port=1883, topic='', qos=0, keepalive=60, *args, **kwargs):
        self.logger = self._init_logger()
        self.broker = broker
        self.port = port
        self.topic = topic
        self.qos = qos
        self.keepalive = keepalive
        mqtt.Client.__init__(self, *args, **kwargs)
        self.steadycam = SteadyCam(basepath, hostname)
        self.last_pic = ''

    def _init_logger(self):
        logger = logging.getLogger('mqtt_shutter')
        logger.info('mqtt_shutter logger instantiated')
        return logger

    def on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode()
        self.logger.debug('message received')
        self.logger.debug('topic: {}  QOS: {}  payload: {}'.format(msg.topic, str(msg.qos), payload))

        if msg.topic == 'shutter' and payload == '1':
            self.logger.info('received snap pic command')
            
            # only delete a pic if we've already taken one
            if self.last_pic: 
                self.steadycam.delete_pic(self.last_pic)
            
            self.last_pic = self.steadycam.snap_pic()
            self.steadycam.transfer_pics(self.last_pic)

    def run(self):
        self.connect(self.broker, self.port, self.keepalive)
        self.subscribe(self.topic, self.qos)

        response_code = 0
        while response_code == 0:
            response_code = self.loop()
        return response_code
