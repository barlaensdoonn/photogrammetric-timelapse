#!/usr/bin/python3
# publish trigger command to MQTT
# 8/25/18
# updated 8/25/18

import paho.mqtt.client as mqtt


broker = 'photogram00.local'
port = 1883
keepalive = 60
topic = 'test'
qos = 2


if __name__ == '__main__':
    client = mqtt.Client()
    client.connect_async(broker, port, keepalive)
    client.loop_start()

    msg = 'testing'
    client.publish(topic, payload=msg, qos=qos)
