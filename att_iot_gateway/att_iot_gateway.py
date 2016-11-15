# -*- coding: utf-8 -*-

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

#for documentation about the mqtt lib, check https://pypi.python.org/pypi/paho-mqtt/0.9
import paho.mqtt.client as mqtt                # provides publish-subscribe messaging support
import calendar                                # for getting the epoch time
from datetime import datetime                  # for json date time
import time                                    # gets the current time
import httplib                                 # for http comm
import urllib                                   # for cleaning up urls (strings and stuff)
from socket import error as SocketError         # for http error handling
import errno                                    # for http error handling
import logging
import socket                                  # for checking if there is support for https
import types as types                          # to check on type info
import json                                    # in case the data we need to send is complex
import unicodedata                              # for converting unicode to regular strings

logger = logging.getLogger('att_iot_gateway')

def _on_connect(client, userdata, rc):
    'The callback for when the client receives a CONNACK response from the server.'

    if rc == 0:
        msg = "Connected to mqtt broker with result code "+str(rc)
        logger.info(msg)
    else:
        logger.error("Failed to connect to mqtt broker, error: " + mqtt.connack_string(rc))
        return

    topic = 'client/' + ClientId + "/in/gateway/" + GatewayId + "/#/command"                                           #subscribe to the topics for the device
    #topic = '#'
    logger.info("subscribing to: " + topic)
    result = _mqttClient.subscribe(topic)                                                    #Subscribing in _on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    logger.info(result)
    if on_connected:
        on_connected()


def _on_MQTTmessage(client, userdata, msg):
    'The callback for when a PUBLISH message is received from the server.'

    payload = str(msg.payload)
    logger.info("Incoming message - topic: " + msg.topic + ", payload: " + payload)
    topicParts = msg.topic.split("/")
    if on_message is not None:
        try:
            if len(topicParts) >= 7:
                if topicParts[5] == 'device':   # 3
                    devId = topicParts[6]       # 4
                    assetId = topicParts[8]
                else:
                    devId = None
                    assetId = topicParts[6]
                on_message(devId, assetId, msg.payload)                                 #we want the second last value in the array, the last one is 'command'
            else:
                logger.error("unknown topic format: " + msg.topic)
        except:
            logger.exception("failed to process actuator command: " + msg.topic + ", payload: " + msg.payload)

def _on_MQTTSubscribed(client, userdata, mid, granted_qos):
    logger.info("Subscribed to topic, receiving data from the cloud: qos=" + str(granted_qos))


#private reference to the mqtt client object for which we reserve a mem loc from the start
_mqttClient = None
_httpServerName = None
_secureHTTP = False
_httpClient = None

# gateway specific stuff
_RegisteredGateway = False                                              # when true: gateway is created in cloud, when false, gateway is not created in cloud, only 'loose' devices are managed. User specified all credentials manually (not adviced)


#has to be provided by the module consumer:

on_message = None
'callback for receiving values from the IOT platform: expects 3 params: deviceId, assetId, payload'
ClientId = None
'the id of the client on the ATT platform, used to connect to the http & mqtt servers'
ClientKey = None
'the key that the ATT platform generated for the specified client'
GatewayId = None
'the id of the gateway that we are using.'


#optionally provided by the module consumer
on_connected = None
'callback that will be signalled once the broker is connected. This can be used to block' \
'the application untill a connection with the broker has been made, so that no data gets lost'


def connect(httpServer="api.AllThingsTalk.io", secure=False, certFile = None):
    """Create a connection with the http server
    :param httpServer: The dns name of the server to use for HTTP communication
    :type httpServer: basestring
    :param secure: When true, an SSL connection will be used, if available.
    """
    global _httpClient, _httpServerName, _secureHTTP                                         # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    if secure == True and hasattr(socket, "ssl") == True:
        logging.info("is secure {}, ssl: {}".format(secure, hasattr(socket, "ssl")))
        _secureHTTP = True
        if certFile:
            _httpClient = httplib.HTTPSConnection(httpServer, cert_file = certFile)
        else:
            _httpClient = httplib.HTTPSConnection(httpServer)
    else:
        _secureHTTP = False
        _httpClient = httplib.HTTPConnection(httpServer)
    _httpServerName = httpServer
    logger.info("connected with http server")

def addAsset(id, deviceId, name, description, type, profile, style = "Undefined"):
    '''add an asset to the device. Use the specified name and description.
    :param id: <type>string</type> The local id of the asset (it's name)
    :type id: basestring
    :param deviceId: The local id of the device that owns the asset (the name of the device)
    :param name: A label for the asset.
    :param description: A desccription.
    :param type: type of asset: sensor, actuator, config, virtual
    :param profile: The data type of the asset: integer, string, number, boolean, json schema definition
    :param style: An optional label that you can attach to the asset, which indicates it's function. Currently supported values are:
        1. Undefined: the asset has no specific style (default)
	    1. Primary: the asset is considered to represent the primary function of the device.
	    1. Config: the asset is used to configure the device.
	    1. Battery: the asset represents a battery value
	    1. Secondary: the asset represents secondary functionality of the device
    :type style: string
    :return: True when succesful (200 ok was returned), otherwise False
    Can raise exceptions when there were network issues.
    '''

    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')

    def getProfile():
        """
        :return: the profile as it can be used in a dict object.
        """
        if isinstance(profile, dict):
            return profile
        elif isinstance(profile, basestring):
            if profile[0] == '{':      # if the asset type is complex (starts with {', then render the body a little different
                return json.loads(profile)
            else:
                return {"type": profile}

    body = {"title": name,
            'description': description,
            'style': style,
            'is':type,
            'profile': getProfile()}
    body = json.dumps(body)

    headers = _buildHeaders()
    url = "/device/" + deviceId + "/asset/" + str(id)
    return _sendData(url, body, headers, 'PUT')

def addGatewayAsset(id, name, description, isActuator, assetType, style = "Undefined"):
    '''add an asset to the gateway'''
    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')

    body = '{"title":"' + name + '","description":"' + description + '", "style": "' + style + '","is":"'
    if isActuator:
        body = body + 'actuator'
    else:
        body = body + 'sensor'

    if assetType[0] == '{':                 # if the asset type is complex (starts with {', then render the body a little different
        body = body + '","profile":' + assetType + '}'
    else:
        body = body + '","profile": {"type":"' + assetType + '" }}'
    headers = _buildHeaders()
    url = "/asset/" + str(id)

    return _sendData(url, body, headers, 'PUT')

def deleteAsset(device, id):
    """
    Delete the asset on the cloud with the specified name on the specified device.
    :param device: the local name of the device.
    :param id: the local name of the asset
    :return: True when the operation was successful (returned 204), otherwise False
    """
    if not device:
        raise Exception("DeviceId not specified")
    headers = _buildHeaders()
    url = "/device/" + device  + "/asset/" + str(id)

    return _sendData(url, "", headers, "DELETE", 204)

def deleteGatewayAsset(id):
    """
    Delete the asset on the cloud with the specified name on the specified device.
    :param device: the local name of the device.
    :param id: the local name of the asset
    :return: True when the operation was successful (returned 204), otherwise False
    """
    headers = _buildHeaders()
    url = "/device/" + str(id)

    return _sendData(url, "", headers, "DELETE", 204)

def addDevice(deviceId, name, description, activateActivity = False):
    '''creates a new device in the IOT platform.
    if the device already exists, the function will fail
    :rtype : None
    :param deviceId: The local identifier of the device
    :param name: the name of the device
    :param description: a description
    :param activateActivity: When true, historical data will be recorded for this device.
    :type activateActivity: bool
    :return True if the operation was succesful, otherwise False
    '''

    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')
    if name:
        body = '{"title":"' + name + '","description":"' + description + '", "type": "custom", "activityEnabled": ' + str(activateActivity).lower() + '}'
    else:
        body = '{"description":"' + description + '", "type": "custom", "activityEnabled": ' + str(activateActivity).lower() + '}'
    headers = _buildHeaders()
    url = "/device/" + str(deviceId)                                    # make certain that the deviceId is a string.

    return _sendData(url, body, headers, 'PUT')


def addDeviceFromTemplate(deviceId, templateId, values):
    """add a device to the cloud by using a predefined template that is stored in the cloud
    :type deviceId: string or int
    :param deviceId:
    :param templateId: the id of the template that should be used
    :type templateId: basestring
    :param values: any optional values that have to be replaced in the template. This is specified as a
                    dictionary with key-value pairs.
    :type values: dictionary (json object)
    :return: the definition of the device that was created (json/dictionary) or None if the template was not found
    """
    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')
    if values:
        body = '{"type":"' + templateId + '", "data": ' + json.dumps(values) + '}'
    else:
        body = '{"type":"' + templateId + '" }'
    headers = _buildHeaders()
    url = "/device/" + deviceId

    return _getData(url, body, headers, 'PUT')

def deviceExists(deviceId):
    '''checks if the device already exists in the IOT platform.
    :param deviceId: the local name of the device.
    :return True when it already exists, otherwise False'''

    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')

    headers = _buildHeaders()
    url = "/device/" + deviceId

    return _sendData(url, "", headers, 'GET')


def deleteDevice(deviceId):
    '''
        Deletes the specified device from the cloud.
        :param deviceId: the local name of the device.
        :return true when successful.
    '''
    headers = _buildHeaders()
    url = "/Device/" + deviceId

    return _sendData(url, "", headers, "DELETE", 204)

def createGateway(name, uid, assets = None):
    """Create a new orphan gateway in the cloud. After the gateway has been created, the user should claim it from within the website so that the gateway is assigned to the correct user account.  To finish the claim procedure, the gateway application should call 'finishclaim' after creating the gateway in the cloud.
When the gateway has ben succesfully created, use 'authenticate' to verify that the gateway still exists in the cloud whenever the gateway restarts.
    :param name: the name ofhte gateway.
    :param uid: a globally unique id for gateways (ex: mac address)
    :param assets: a json structure with all the assets that should be created for the gateway. Default is None
    :return: True when succesfull.
    """

    if assets == None:
        body = '{"uid":"' + uid + '","name":"' + name + '", "assets":[] }'
    else:
        body = '{"uid":"' + uid + '","name":"' + name + '", "assets":' + json.dumps(assets) + ' }'
    headers = {"Content-type": "application/json"}
    url = "/gateway"
    return _sendData(url, body, headers)

def getGateway(includeDevices = True):
    headers = _buildHeaders()
    url = '/gateway/' + GatewayId + '?includeDevices=' + str(includeDevices)

    return _getData(url, "", headers)

def finishclaim(name, uid):
    '''finish the claiming process for a previously created gateway.  When done, the system will store the credentials
    return true if succesful, otherwise false'''
    body = '{"uid":"' + uid + '","name":"' + name + '" , "assets":[]}'
    headers = {"Content-type": "application/json"}
    url = "/gateway"
    url = urllib.quote(url, '/?=')

    logger.info("HTTP POST: " + url)
    logger.info("HTTP HEADER: " + str(headers))
    logger.info("HTTP BODY:" + body)

    try:
        _httpClient.request('POST', url, body, headers)
        response = _httpClient.getresponse()
    except:
        logger.exception("finishClaim")
        _reconnectAfter('finishClaim')                                             # recreate the connection when something went wrong. if we don't do this and an error occured, consecutive requests will also fail.
        return False
    status = response.status
    logger.info((status, response.reason))
    response = response.read()
    logger.info(response)
    if status == 200:
        _storeCredentials(json.loads(response))
        return True
    else:
        return False

def getAssetState(assetId, deviceId):
    '''look up the current state value for the asset with the specified local id, on the specified device (local id)
    :return json object. If not found, returns None'''

    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')
    headers = _buildHeaders()
    url = "/device/" + deviceId + "/asset/" + str(assetId) + "/state"

    return _getData(url, "", headers)

def _buildPayLoadHTTP(value):
    data = {"value": value, "at": datetime.utcnow().isoformat()  + 'Z'}
    return json.dumps(data)


def _storeCredentials(gateway):
    'extracts all the relevant info from the gateway response object'
    global GatewayId
    global ClientKey
    global ClientId
    global _RegisteredGateway
    GatewayId = unicodedata.normalize('NFKD', gateway["id"]).encode('ascii','ignore')       #convert to regular strings (from unicode), if we don't do this, the mqtt subscribe fails (can't handle unicode as it's uid for the session)
    ClientKey = unicodedata.normalize('NFKD', gateway["key"]).encode('ascii','ignore')
    ClientId = unicodedata.normalize('NFKD', gateway["client"]["clientId"]).encode('ascii','ignore')
    _RegisteredGateway = True                                   # so we know that we are using a registered gateway.

def authenticate():
    '''validate that the currently stored credentials are ok.
        :return True if succesful, otherwise False'''

    headers = _buildHeaders()
    url = "/gateway"

    global _RegisteredGateway
    if _sendData(url, "", headers, 'GET'):
        _RegisteredGateway = True
        return True
    else:
        _RegisteredGateway = False
        return False

def _reconnectAfter(caller):
    try:
        _httpClient.close()
        connect(_httpServerName, _secureHTTP)                # recreate the connection when something went wrong. if we don't do this and an error occured, consecutive requests will also fail.
    except:
        logger.exception("reconnect failed after " + caller + " produced an error")

def _sendData(url, body, headers, method = 'POST', status = 200):
    """send the data and check the result
        Some multi threading applications can have issues with the server closing the connection, if this happens
        we try again
    """
    url = urllib.quote(url, '/?=')

    logger.info("HTTP " + method + ": " + url)
    logger.info("HTTP HEADER: " + str(headers))
    logger.info("HTTP BODY:" + str(body))                   # could be none

    success = False
    badStatusLineCount = 0  # keep track of the amount of 'badStatusLine' exceptions we received. If too many raise to caller, otherwise retry.
    while not success:
        try:
            _httpClient.request(method, url, body, headers)
            response = _httpClient.getresponse()
            logger.info((response.status, response.reason))
            logger.info(response.read())
            return response.status == status
        except httplib.BadStatusLine:  # a bad status line is probably due to the connection being closed. If it persists, raise the exception.
            badStatusLineCount += 1
            if badStatusLineCount < 10:
                _reconnectAfter("_sendData")
            else:
                raise
        except SocketError as e:
            _reconnectAfter("_sendData")
            if e.errno != errno.ECONNRESET:             # if it's error 104 (connection reset), then we try to resend it, cause we just reconnected
                raise
        except:
            _reconnectAfter("_sendData")
            raise

def _getData(url, body, headers, method = 'GET', status = 200):
    """send a request to the server and return the response"""
    success = False
    badStatusLineCount = 0  # keep track of the amount of 'badStatusLine' exceptions we received. If too many raise to caller, otherwise retry.
    url = urllib.quote(url, '/?=')

    logger.info("HTTP " + method + ': ' + url)
    logger.info("HTTP HEADER: " + str(headers))
    logger.info("HTTP BODY:" + body)

    while not success:
        try:
            _httpClient.request(method, url, body, headers)
            response = _httpClient.getresponse()
            logger.info((response.status, response.reason))
            result = response.read()
            logger.info(result)
            if response.status == status:
                if result:
                    return json.loads(result)
                else:
                    return None
            else:
                return None
        except httplib.BadStatusLine:  # a bad status line is probably due to the connection being closed. If it persists, raise the exception.
            badStatusLineCount += 1
            if badStatusLineCount < 10:
                _reconnectAfter("_sendData")
            else:
                raise
        except SocketError as e:
            _reconnectAfter("_getData")
            if e.errno != errno.ECONNRESET:  # if it's error 104 (connection reset), then we try to resend it, cause we just reconnected
                raise
        except:
            _reconnectAfter("_getData")
            raise

def _buildHeaders():
    return {"Content-type": "application/json", "Auth-GatewayKey": ClientKey, "Auth-GatewayId": GatewayId}


def subscribe(mqttServer = "api.AllThingsTalk.io", port = 1883, secure = False, certFile = 'cacert.pem'):
    '''start the mqtt client and make certain that it can receive data from the IOT platform
	   :param mqttServer:  the address of the mqtt server. Only supply this value if you want to a none standard server. Default = broker.AllThingsTalk.io
	   :param port: the port number to communicate on with the mqtt server. Default = 1883
	   :param secure: When true, an SSL connection is used. Default = False.  When True, use port 8883 on broker.AllThingsTalk.io
	   :param certFile: certfile is a string pointing to the PEM encoded client
        certificate and private keys respectively. Note
        that if either of these files in encrypted and needs a password to
        decrypt it, Python will ask for the password at the command line. It is
        not currently possible to define a callback to provide the password.
	   Note: SSL will can only be used when the mqtt lib has been compiled with support for ssl
    '''
    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')

    global _mqttClient                                             # we assign to this var first, so we need to make certain that they are declared as global, otherwise we create new local vars
    if len(GatewayId) > 23:
        mqttId = GatewayId[:23]
    else:
        mqttId = GatewayId
    _mqttClient = mqtt.Client(mqttId)
    _mqttClient.on_connect = _on_connect
    _mqttClient.on_message = _on_MQTTmessage
    _mqttClient.on_subscribe = _on_MQTTSubscribed
    if ClientId is None:
        logger.error("ClientId not specified, can't connect to broker")
        raise Exception("ClientId not specified, can't connect to broker")
    brokerId = ClientId + ":" + ClientId
    _mqttClient.username_pw_set(brokerId, ClientKey);
    if secure and socket.ssl:
        _mqttClient.tls_set(certFile)
    _mqttClient.connect(mqttServer, port, 60)
    _mqttClient.loop_start()

def _buildPayLoad(value):
    typeOfVal = type(value)
    if typeOfVal in [types.IntType, types.BooleanType, types.FloatType, types.LongType, types.StringType]:      # if it's a basic type: send as csv, otherwise as json.
        timestamp = calendar.timegm(time.gmtime())                                # we need the current epoch time so we can provide the correct time stamp.
        return str(timestamp) + "|" + str(value)                                            # build the string that contains the data that we want to send
    else:
        data = {  "value": value, "at": datetime.utcnow().isoformat() + 'Z' }       # the +Z is a small hack cause utcnow doesn't include timezone info. Since we want utc time, we can add the value 'z' to indicate this.
        return json.dumps(data)



def send(value, deviceId, assetId):
    """send the data to the cloud. Data can be a single value or object
    :param value: the value to send in the form of a string. So a boolean is sent as 'true' or 'false', an integer can be sent as '1' and a fload as '1.1'.  You can also send an object or a python list with this function to the cloud. Objects will be converted to json objects, lists become json arrays. The fields/records in the json objects or arrays must be the same as defined in the profile.
    :type value: string or json object
    :param deviceId: The local name of the device
    :param assetId: the local name of the asset
    """
    if ClientId is None:
        logger.error("ClientId not specified")
        raise Exception("ClientId not specified")
    if assetId is None:
        logger.error("sensor id not specified")
        raise Exception("sensorId not specified")
    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')

    toSend = _buildPayLoad(value)
    topic = "client/" + ClientId + "/out/gateway/" + GatewayId
    if deviceId != None:
        topic += "/device/" + deviceId + "/asset/" + str(assetId) + "/state"             # also need a topic to publish to
    else:
        topic += "/asset/" + str(assetId) + "/state"
    logger.info("Publishing message - topic: " + topic + ", payload: " + toSend)
    _mqttClient.publish(topic, toSend, 0, False)


def sendCommand(value, gatewayId, deviceId, assetId):
    """send the data to the cloud. Data can be a single value or object
    :param value: the value to send in the form of a string. So a boolean is sent as 'true' or 'false', an integer can be sent as '1' and a fload as '1.1'.  You can also send an object or a python list with this function to the cloud. Objects will be converted to json objects, lists become json arrays. The fields/records in the json objects or arrays must be the same as defined in the profile.
    :type value: string or json object
    :param deviceId: The local name of the device
    :param assetId: the local name of the asset
    """
    if ClientId is None:
        logger.error("ClientId not specified")
        raise Exception("ClientId not specified")
    if assetId is None:
        logger.error("sensor id not specified")
        raise Exception("sensorId not specified")
    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')

    typeOfVal = type(value)
    if typeOfVal in [types.IntType, types.BooleanType, types.FloatType, types.LongType, types.StringType]:  # if it's a basic type: send as csv, otherwise as json.
        toSend = str(value)
    else:
        toSend = json.dumps(value)
    topic = "client/" + ClientId + "/in/"
    if gatewayId:
        topic += "gateway/" + gatewayId
    if deviceId != None:
        topic += "/device/" + deviceId + "/asset/" + str(assetId) + "/command"             # also need a topic to publish to
    else:
        topic += "/asset/" + str(assetId) + "/command"
    logger.info("Publishing message - topic: " + topic + ", payload: " + toSend)
    _mqttClient.publish(topic, toSend, 0, False)


def sendValueHTTP(value, deviceId, assetId):
    '''Sends a new value for an asset over http. This function is similar to send, accept that the latter uses mqtt
       while this function uses HTTP

       Parameters are the same as for the send function.
       '''
    if _RegisteredGateway == False:
        raise Exception('gateway must be registered')

    body = _buildPayLoadHTTP(value)
    headers = _buildHeaders()
    url = "/device/" + deviceId + "/asset/" + str(assetId) + "/state"

    return _sendData(url, body, headers, 'PUT')