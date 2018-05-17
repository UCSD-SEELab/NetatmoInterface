import paho.mqtt.client as mqtt
import json
import time
import configparser
from code import interact


def start_device(device_id='NetatmoBE50'):
    dict_start_msg = {
        'device_id': device_id,
        'b_running': True
    }
    print("START {0}".format(device_id))
    client.publish(device_id + '/control', payload=json.dumps(dict_start_msg))


def stop_device(device_id='NetatmoBE50'):
    dict_stop_msg = {
        'device_id': device_id,
        'b_running': False
    }
    print("STOP {0}".format(device_id))
    client.publish(device_id + '/control', payload=json.dumps(dict_stop_msg))


def process_message(client, userdata, message):  # add callback function
    data = message.payload
    msg = json.loads(message.payload)
    print('MQTT: message received')
    #print('MQTT: {0} {1}'.format(message.topic, str(message.payload)))
    print('MQTT: {0} {1}'.format(message.topic, msg))


if __name__ == '__main__':

    config = configparser.RawConfigParser()
    config.read('config.cfg')

    # Parse config file
    mac_address = config.get('User', 'mac_address')
    device = 'Netatmo' + mac_address[12:].replace(":", "").upper()

    broker_address = 'iot.eclipse.org'

    # Setup MQTT connection
    client = mqtt.Client(client_id='NetatmoController',
                         clean_session=True,
                         protocol=mqtt.MQTTv31)  # additional parameters for clean_session, userdata, protection,

    client.on_message = process_message
    print('MQTT: Connecting to broker {0}'.format(broker_address))
    client.connect(broker_address, port=1883)
    print('MQTT connected')
    client.loop_start()  # start the loop
    topic_ctl = device + '/control'
    topic_data = device + '/raw'
    print('MQTT: Subscribing to topic {0}'.format(topic_ctl))
    client.subscribe(topic_data)

    interact(local=locals())

    client.loop_stop()


