#!/usr/bin/python3
# process trigger command passed over MQTT
# 8/25/18
# updated 8/27/18

import logging
import paho.mqtt.client as mqtt


class MQTTCam(mqtt.Client):

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

    def on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode()
        self.logger.info('topic: {}   QOS: {}   payload: {}'.format(msg.topic, str(msg.qos), payload))

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
