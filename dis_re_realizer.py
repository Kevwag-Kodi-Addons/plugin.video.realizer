#!/usr/bin/python3
import requests
import json
import sys
import base64

kodi_credentials = b'kodi:Badger2007' 
kodi_encoded_credentials = base64.b64encode(kodi_credentials) 
kodi_authorization = b'Basic ' + kodi_encoded_credentials 
kodi_header = { 'Content-Type': 'application/json', 'Authorization': kodi_authorization } 
kodi_ip = '127.0.0.1'
kodi_port = '8080'
kodi_url = 'http://' + kodi_ip + ':' + kodi_port + '/jsonrpc'



kodi_params = ('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":8,"params":{"addonid":"plugin.video.realizer","enabled":false}}')
kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
json_object  = json.loads(json_data)
print(json_object['result'])
kodi_params = ('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":8,"params":{"addonid":"plugin.video.realizer","enabled":true}}')
kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
json_object  = json.loads(json_data)
print(json_object['result'])
