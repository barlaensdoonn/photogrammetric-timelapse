#!/usr/bin/python3
# process trigger command passed over MQTT
# 8/25/18
# updated 8/28/18

import os
import logging
import subprocess
from time import sleep
from datetime import datetime
from picamera import PiCamera
import paho.mqtt.client as mqtt


class MQTTCam(mqtt.Client):

    def __init__(self, hostname, basepath, broker='mqtt-broker.local', port=1883, topic='', qos=0, keepalive=60, *args, **kwargs):
        self.logger = self._init_logger()
        self.hostname = hostname
        self.basepath = basepath
        self.broker = broker
        self.port = port
        self.topic = topic
        self.qos = qos
        self.keepalive = keepalive
        mqtt.Client.__init__(self, *args, **kwargs)

    def _init_logger(self):
        logger = logging.getLogger('mqtt_cam')
        logger.info('mqtt_cam logger instantiated')
        return logger

    def snap_pic(self):
        self.logger.info('time entering snap_pic(): {}'.format(datetime.now()))
        self.logger.info('snapping a pic')

        with PiCamera(resolution=(2592, 1944)) as cam:
            sleep(2)
            now = datetime.now()
            self.logger.info('time before capture: {}'.format(datetime.now()))
            pic = os.path.join(self.basepath, '{}_{}.jpg'.format(self.hostname, now.strftime("%Y-%m-%d_%H-%M")))
            cam.capture(pic)
            self.logger.info('time after capture: {}'.format(datetime.now()))
            self.logger.info('snapped a pic')

        return pic

    def copy_pic(self, pic_path):
        remote_host = 'pi@{}:~'.format(self.broker)
        remote_pic_path = os.path.join(remote_host, 'test_pics')
        status = subprocess.call(['scp', '-p', pic_path, remote_pic_path], stdout=subprocess.DEVNULL)

        if status == 0:
            self.logger.info('copied {} to {}'.format(pic_path.split('/')[-1], remote_pic_path))

    def on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode()
        self.logger.info('message received')
        self.logger.info('topic: {}  QOS: {}  payload: {}'.format(msg.topic, str(msg.qos), payload))

        if msg.topic == 'shutter' and payload == '1':
            snapped = self.snap_pic()
            self.copy_pic(snapped)

    def run(self):
        self.connect(self.broker, self.port, self.keepalive)
        self.subscribe(self.topic, self.qos)

        response_code = 0
        while response_code == 0:
            response_code = self.loop()
        return response_code


if __name__ == '__main__':
    client = MQTTCam(broker='photogram00.local', topic='shutter', qos=2)
    client.run()
