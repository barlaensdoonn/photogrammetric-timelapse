#!/usr/bin/python3
# process trigger command passed over MQTT
# 8/25/18
# updated 8/27/18

import os
import logging
from time import sleep
from datetime import datetime
from picamera import PiCamera
import paho.mqtt.client as mqtt


def get_basepath():
    '''we need the absolute path when running scripts as a systemd service'''
    return os.path.dirname(os.path.realpath(__file__))


class MQTTCam(mqtt.Client):

    basepath = get_basepath()

    def __init__(self, broker='mqtt-broker.local', port=1883, topic='', qos=0, keepalive=60, *args, **kwargs):
        self.logger = self._init_logger()
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
        self.logger.info('snapping a pic')

        with PiCamera(resolution=(2592, 1944)) as cam:
            sleep(2)
            now = datetime.now()
            cam.capture(os.path.join(self.basepath, '{}.jpg'.format(now.strftime("%Y-%m-%d_%H-%M"))))
            self.logger.info('snapped a pic')

    def on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode()
        self.logger.info('message received')
        self.logger.info('topic: {}  QOS: {}  payload: {}'.format(msg.topic, str(msg.qos), payload))

        if msg.topic == 'shutter' and payload == '1':
            self.snap_pic()

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
