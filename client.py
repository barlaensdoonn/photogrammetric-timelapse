#!/usr/bin/python3
# process trigger command passed over MQTT
# 8/25/18
# updated 8/25/18

import paho.mqtt.client as mqtt


broker = 'photogram00.local'
port = 1883
keepalive = 60
topic = 'test'
qos = 2


class MQTTClientReference(mqtt.Client):
    '''
    original client class from paho.mqtt.python examples. more here:
    http://www.eclipse.org/paho/clients/python/
    '''

    def on_connect(self, mqttc, obj, flags, rc):
        print('response code: {}'.format(str(rc)))

    def on_message(self, mqttc, obj, msg):
        print('topic: {}   QOS: {}   payload: {}'.format(msg.topic, str(msg.qos), str(msg.payload)))

    def on_publish(self, mqttc, obj, mid):
        print('mid: {}'.format(str(mid)))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print('subscribed: {}   granted_QOS: {}'.format(str(mid), str(granted_qos)))

    def on_log(self, mqttc, obj, level, string):
        print('log: {}'.format(string))

    def run(self):
        self.connect(broker, port, keepalive)
        self.subscribe(topic, qos)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc


if __name__ == '__main__':
    client = MQTTClientReference()
    client.run()
