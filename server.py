#!/usr/bin/python3
# publish trigger command to MQTT
# 8/25/18
# updated 8/27/18

import paho.mqtt.publish as publish


if __name__ == '__main__':
    broker = 'photogram00.local'
    topic = 'shutter'
    qos = 2
    msg = 1
    publish.single(topic, msg, hostname=broker, qos=qos)
