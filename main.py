#!/usr/bin/python3
# publish trigger command to MQTT
# 8/25/18
# updated 8/31/18

import os
import sys
import yaml
import logging
import logging.config
from time import sleep
from socket import gethostname
import paho.mqtt.publish as publish
from mqtt_shutter import MQTTShutter


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
    basepath = get_basepath()
    logger = configure_logger(basepath, hostname)
    broker = 'photogram00.local'
    topic = 'shutter'
    qos = 2
    msg = 1

    try:
        if hostname in broker:
            # if we are the broker, publish snap pic command indefinitely
            while True:
                logger.info('publishing msg {} to topic {}'.format(msg, topic))
                publish.single(topic, msg, hostname=broker, qos=qos)
                sleep(10)
        else:
            # if we're not the broker then we should have a camera and be listening for shutter commands
            try:
                client = MQTTShutter(basepath, hostname, broker=broker, topic=topic, qos=2)
                client.run()
            except Exception:
                logger.error('exception!!')
                raise
            finally:
                # shutdown our camera to prevent GPU memory leak
                client.steadycam.close()
    except KeyboardInterrupt:
        logger.info('user exit received...')
        logger.info('exiting')
        sys.exit()
