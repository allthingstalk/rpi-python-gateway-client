#!/usr/bin/python

#   Copyright 2014-2016 AllThingsTalk
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# in this example, a basic gateway is created in the cloud and tries to create a single device, with a single asset and send a single value to the cloud
# the setup is done in such a way that the gateway continuously tries to discover new devices and create them in the cloud -> this can be used as a basic starting point for proper gateway devices.

import logging
logging.getLogger().setLevel(logging.INFO)

from time import sleep                             #pause the app
from ConfigParser import *
from uuid import getnode as get_mac
import att_iot_gateway.att_iot_gateway as IOT                              #provide cloud support

def connect():
    'set up the connection with the cloud + register the gateway'
    IOT.on_message = on_message
    IOT.connect()          
    if authenticate():
        IOT.subscribe()              							#starts the bi-directional communication  
    else:
        raise Exception("Failed to authenticate with IOT platform")

def authenticate(maxClaim = 30):
    '''if authentication had previously succeeded, loads credentials and validates them with the platform
       if not previously authenticated: register as gateway and wait until user has claimed it
       params:
       uid: string = a value that uniquely identifies this device. Usually a mac address
       maxClaim: int = nr of times that system should try to finish the claim (waits for 1second between tries) before timing out if the user has to claim the gateway in the cloud
    '''
    if _tryLoadConfig() == False:
        uid = _getUid();
        IOT.createGateway("generic gateway", uid)
        while True:                                     # we try to finish the claim process until success or app quits, cause the app can't continue without a valid and claimed gateway
            if IOT.finishclaim("generic gateway", uid):
                _storeConfig()
                sleep(2)                                # give the platform a litle time to set up all the configs so that we can subscribe correctly to the topic. If we don't do this, the subscribe could fail
                return True
            else:
                sleep(1)
        return False                                # if we get here, didn't succeed in time to finish the claiming process.
    else:
        if IOT.authenticate():
            print('Authenticated')
            return True
        else:
            print('failed to authenticate')
            return False

def _tryLoadConfig():
    'load the config from file'
    c = ConfigParser()
    if c.read('gateway.config'):
        IOT.GatewayId = c.get('general', 'gatewayId')
        IOT.ClientId = c.get('general', 'clientId')
        IOT.ClientKey = c.get('general', 'clientKey')
        return True
    else:
        return False

def _storeConfig():
    "store the current gateway settings in a config file"
    c = ConfigParser()
    c.add_section('general')
    c.set('general', 'gatewayId', IOT.GatewayId)
    c.set('general', 'clientId', IOT.ClientId)
    c.set('general', 'clientKey', IOT.ClientKey)

    with open('gateway.config', 'w') as f:
        c.write(f)

def _getUid():
    'extract the mac address in order to identify the gateway in the cloud'
    mac = 0
    while True:                                                                     # for as long as we are getting a fake mac address back, try again (this can happen if the hw isn't ready yet, for instance usb wifi dongle)
        mac = get_mac()
        if mac & 0x10000000000 == 0:
            break
        sleep(1)                                                                    # wait a bit before retrying.

    result = hex(mac)[2:-1]                                                         # remove the 0x at the front and the L at the back.
    while len(result) < 12:                                                         # it could be that there were missing '0' in the front, add them manually.
        result = "0" + result
    result = result.upper()                                                         # make certain that it is upper case, easier to read, more standardized
    print('mac address: ' + result)
    return result


#callback: handles values sent from the cloudapp to the device
def on_message(device, actuator, value):
    print("received: " + value + ", for device: " + device + ", actuator: " + actuator)

devices = []                                           #contains the list of devices already connected to the


connect()
while True:
    try:
        deviceId = '1'
        if deviceId not in devices:                     										#if we haven't seen this deviceId yet, check if we need to create a new device for it
            devices.append(deviceId)
            print "Check if device already known in IOT"
            if IOT.deviceExists(deviceId) == False:     										#as we only keep deviceId's locally in memory, it could be that we already created the device in a previous run. We only want to create it 1 time.
                print "creating new device"
                IOT.addDevice(deviceId, 'name of the device', "description of the device" )		#adjust according to your needs
                IOT.addAsset(1, deviceId, 'relay', 'switch something on/off', True, 'boolean')	#adjust according to your needs
                IOT.send("true", deviceId, 1)
		sleep(3)
    except KeyboardInterrupt:                                                    				#stop the script
        break
    except ValueError as e:                                                      				#in case of an xbee error: print it and try to continue
        print e

