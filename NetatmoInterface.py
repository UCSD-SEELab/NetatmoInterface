#!/usr/bin python
# This code sample uses requests (HTTP library)
import requests
import configparser
import time
import paho.mqtt.client as mqtt
import json


class NetatmoSensor:

    def __init__(self, id):
        self.device_id = id
        self.temperature = 0
        self.humidity = 0
        self.pressure = 0
        self.time_utc = 0
        self.co2 = 0
        self.noise = 0
        self.b_running = True
        self.co2_en = True

    def set_data(self, temperature, humidity, pressure, time_utc, co2, noise):
        self.temperature = temperature
        self.noise = humidity
        self.pressure = pressure
        self.time_utc = time_utc
        self.co2 = co2
        self.noise = noise

    def get_json(self):
        dict_parsed_msg = {
            'time_utc': self.time_utc,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'co2': self.co2,
            'noise': self.noise
        }
        return json.dumps(dict_parsed_msg)

    def get_string(self):
        return('{0},{1},{2},{3},{4},{5}'.format(self.time_utc, self.temperature,
                                                self.humidity, self.pressure,
                                                self.co2, self.noise))

    def print_data(self):
        print('Time: {0}  Temp: {1}  Humidity: {2}  Pressure: '
              '{3}  CO2: {4}  Noise: {5}'.format(self.time_utc, self.temperature,
                                                 self.humidity, self.pressure,
                                                 self.co2, self.noise))


config = configparser.RawConfigParser()
config.read('config.cfg')

# Parse config file
email = config.get('User', 'email')
password = config.get('User', 'password')
client_id = config.get('User', 'client_id')
client_secret = config.get('User', 'client_secret')
mac_address = config.get('User', 'mac_address')
broker_address = config.get('User', 'broker_address')
device_id = 'Netatmo' + mac_address[12:].replace(":", "").upper()

sensor = NetatmoSensor(device_id)

payload = {'grant_type': 'password',
           'username': email,
           'password': password,
           'client_id': client_id,
           'client_secret': client_secret,
           'scope': 'read_station'}


def process_message(client, userdata, message):  # add callback function
    print('MQTT: message received')
    data = message.payload
    try:
        msg = json.loads(data)
    except:
        print("MQTT message parse failure")
        return

    if 'b_running' in msg:
        sensor.b_running = msg['b_running']
        print('MQTT: {0} running = {1}'.format(message.topic, msg['b_running']))
    else:
        print('MQTT: {0} {1}'.format(message.topic, str(data)))


# Setup MQTT connection
client = mqtt.Client(client_id=device_id,
                     clean_session=True,
                     protocol=mqtt.MQTTv31)  # additional parameters for clean_session, userdata, protection,
client.on_message = process_message
print('MQTT: Connecting to broker {0}'.format(broker_address))
client.connect(broker_address, port=1883)
client.loop_start()  # start the loop
topic_ctl = device_id + '/control'
topic_data = device_id + '/raw'
print('MQTT: Subscribing to topic {0}'.format(topic_ctl))
client.subscribe(topic_ctl)

# TODO: classes
# TODO: control: en, disable, time,
# TODO: command line arguments/ script sys.argv, getopt

try:
    response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
    response.raise_for_status()
    access_token = response.json()["access_token"]

    # TODO: use refresh_token after 3 hours
    refresh_token = response.json()["refresh_token"]
    expires_in = response.json()["expires_in"]
    scope = response.json()["scope"]
    # print("Your refresh token is:", refresh_token)
    # print("Your token expires in:", expires_in)
    # print("Your scopes are:", scope)

    params = {'access_token': access_token,
              'device_id': mac_address}

    t_last_msg = time.time()
    while True:
        response = requests.post("https://api.netatmo.com/api/getstationsdata", params=params)
        response.raise_for_status()
        data = response.json()["body"]["devices"][0]["dashboard_data"]

        while not sensor.b_running:
            print("Stopped by control")
            time.sleep(10)

        if time.time() - t_last_msg > 10:
            t_last_msg = time.time()
            sensor.set_data(data['Temperature'], data['Humidity'], data['Pressure'],
                            data['time_utc'], data['CO2'], data['Noise'])

            sensor.print_data()
            with open(sensor.device_id + '.csv', 'a') as csv_file:
                csv_file.write(sensor.get_string() + "\n")
            client.publish(topic_data, payload=sensor.get_json())

        time.sleep(1)

except requests.exceptions.HTTPError as error:
    print(error.response.status_code, error.response.text)

client.loop_stop()
