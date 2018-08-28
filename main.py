#!/usr/bin/python3
# publish trigger command to MQTT
# 8/25/18
# updated 8/27/18

import os
import yaml
import logging
import logging.config
from socket import gethostname
import paho.mqtt.publish as publish
from mqtt_cam import MQTTCam


def _get_logfile_name(basepath, hostname):
    '''format log file as "hostname.log"'''
    return os.path.join(basepath, '{}.log'.format(hostname))


def _init_logger():
    logger = logging.getLogger('main')
    logger.info('main logger instantiated')
    return logger


def get_basepath():
    '''we need the absolute path when running scripts as a systemd service'''
    return os.path.dirname(os.path.realpath(__file__))


def get_hostname():
    return gethostname().split('.')[0]


def configure_logger(basepath, hostname):
    with open(os.path.join(basepath, 'log.yaml'), 'r') as log_conf:
        log_config = yaml.safe_load(log_conf)

    log_config['handlers']['file']['filename'] = _get_logfile_name(basepath, hostname)
    logging.config.dictConfig(log_config)
    logging.info('* * * * * * * * * * * * * * * * * * * *')
    logging.info('logging configured')

    return _init_logger()


if __name__ == '__main__':
    hostname = get_hostname()
    logger = configure_logger(get_basepath(), hostname)
    broker = 'photogram00.local'
    topic = 'shutter'
    qos = 2
    msg = 1

    if hostname in broker:
        logger.info('publishing msg {} to topic {}'.format(msg, topic))
        publish.single(topic, msg, hostname=broker, qos=qos)
    else:
        client = MQTTCam(broker=broker, topic=topic, qos=2)
        client.run()
