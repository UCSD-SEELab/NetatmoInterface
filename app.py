#This code sample uses requests (HTTP library)
import requests
import configparser

config = configparser.RawConfigParser()
config.read('example.cfg')

email = config.get('User', 'email')
password = config.get('User', 'password')
client_id = config.get('User', 'client_id')
client_secret = config.get('User', 'client_secret')

payload = {'grant_type': 'password',
           'username': email,
           'password': password,
           'client_id': client_id,
           'client_secret': client_secret,
           'scope': 'read_station'}
try:
    response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
    response.raise_for_status()
    access_token=response.json()["access_token"]
    refresh_token=response.json()["refresh_token"]
    expires_in=response.json()["expires_in"]
    scope=response.json()["scope"]
    print("Your access token is:", access_token)
    print("Your refresh token is:", refresh_token)
    print("Your token expires in:", expires_in)
    print("Your scopes are:", scope)

    params = {'access_token': access_token,
              'device_id': '70:ee:50:20:be:50'}

    response = requests.post("https://api.netatmo.com/api/getstationsdata", params=params)
    response.raise_for_status()
    dashboard_data = response.json()["body"]["devices"][0]["dashboard_data"]
    print(dashboard_data)

except requests.exceptions.HTTPError as error:
    print(error.response.status_code, error.response.text)
