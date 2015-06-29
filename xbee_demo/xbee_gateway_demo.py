#!/usr/bin/python

# not yet supported

import serial
from xbee import ZigBee
from time import sleep                             #pause the app
import logging
from ConfigParser import *
from uuid import getnode as get_mac

import att_iot_gateway as IOT                              #provide cloud support

def connect():
    'set up the connection with the cloud + register the gateway'
    IOT.on_message = on_message
    IOT.connect()           #"att-capp-2.cloudapp.net"
    if authenticate():
        IOT.subscribe()              							#starts the bi-directional communication   "att-2.cloudapp.net"
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
        IOT.createGateway("Liato gateway", uid)
        while True:                                     # we try to finish the claim process until success or app quits, cause the app can't continue without a valid and claimed gateway
            if IOT.finishclaim("Liato gateway", uid):
                _storeConfig()
                sleep(2)                                # give the platform a litle time to set up all the configs so that we can subscribe correctly to the topic. If we don't do this, the subscribe could fail
                return True
            else:
                sleep(1)
        return False                                # if we get here, didn't succeed in time to finish the claiming process.
    else:
        if IOT.authenticate():
            logging.info('Authenticated')
            return True
        else:
            logging.error('failed to authenticate')
            return False

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
    logging.info('mac address: ' + result)
    return result


def _storeConfig():
    "store the current gateway settings in a config file"
    c = ConfigParser()
    c.add_section('general')
    c.set('general', 'gatewayId', IOT.GatewayId)
    c.set('general', 'clientId', IOT.ClientId)
    c.set('general', 'clientKey', IOT.ClientKey)

    with open('../config/gateway.config', 'w') as f:
        c.write(f)

def _tryLoadConfig():
    'load the config from file'
    c = ConfigParser()
    if c.read('../config/gateway.config'):
        IOT.GatewayId = c.get('general', 'gatewayId')
        IOT.ClientId = c.get('general', 'clientId')
        IOT.ClientKey = c.get('general', 'clientKey')
        return True
    else:
        return False

#serial_port = serial.Serial('/dev/ttyUSB0', 9600)        #for linux
serial_port = serial.Serial('COM5', 9600)                 #for windows
zb = ZigBee(serial_port)

#callback: handles values sent from the cloudapp to the device
def on_message(deviceId, assetId, value):
    print "not yet supported"

#make certain that the device & it's features are defined in the cloudapp

devices = []                                           #contains the list of devices already connected to the

connect()
while True:
    try:
        data = zb.wait_read_frame() #Get data for later use
        print "found data: "
        print data
        deviceId = data['source_addr_long'].encode("HEX")
        if deviceId not in devices:                     										#if we haven't seen this deviceId yet, check if we need to create a new device for it
            devices.append(deviceId)
            print "Check if device already known in IOT"
            if IOT.deviceExists(deviceId) == False:     										#as we only keep deviceId's locally in memory, it could be that we already created the device in a previous run. We only want to create it 1 time.
                print "creating new device"
                IOT.addDevice(deviceId, 'name of the device', "description of the device" )		#adjust according to your needs
                IOT.addAsset(1, deviceId, 'asset name', 'asset description', False, 'int')	#adjust according to your needs
                IOT.addAsset(2, deviceId, "asset name", "asset description", False, "int")	#adjust according to your needs
                IOT.addAsset(3, deviceId, "asset name", "asset description", False, "int")	#adjust according to your needs
        IOT.send(data['samples'][0]['adc-1'], deviceId, 1)									#adjust according to your needs
        IOT.send(data['samples'][0]['adc-2'], deviceId, 2)									#adjust according to your needs
        IOT.send(data['samples'][0]['adc-3'], deviceId, 3)									#adjust according to your needs
    except KeyboardInterrupt:                                                    				#stop the script
        break
    except ValueError as e:                                                      				#in case of an xbee error: print it and try to continue
        print e

serial_port.close()																				#when done, close serial port	