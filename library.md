# att_iot_gateway Module


## Data
The following global variables are also needed for the system, but can be supplied by the platform.  You don't have to supply them manually. See the xbee example for more info.
- `ClientId = None` : the account id. This identifies you as the owner of the device.

- `ClientKey = None` : the key that accompanies your account. It is used as a security token for http calls.
- `on_connected = None` : optional callback function that is called when the mqtt connection is established.
- `on_message = None` : the callback function that will be called whenever data is sent from the IOT platform to one of the assets on your device.

## Functions

### addAsset 

```Python
addAsset(id, deviceId, name, description, type, profile, style='Undefined')
``` 

add an asset to the device. Use the specified name and description.

_parameters:_

- `id:` <type>string</type> The local id of the asset (it's name)
<type>type id:</type> basestring
- `deviceId:` The local id of the device that owns the asset (the name of the device)
- `name:` A label for the asset.
- `description:` A desccription.
- `type:` type of asset: sensor, actuator, config, virtual
- `profile:` The data type of the asset: integer, string, number, boolean, json schema definition
- `style:` An optional label that you can attach to the asset, which indicates it's function. Currently supported values are:
  1. Undefined: the asset has no specific style (default)
  1. Primary: the asset is considered to represent the primary function of the device.
  1. Config: the asset is used to configure the device.
  1. Battery: the asset represents a battery value
  1. Secondary: the asset represents secondary functionality of the device
<type>type style:</type> string


_returns_: True when succesful (200 ok was returned), otherwise False
Can raise exceptions when there were network issues. 

### addDevice 

```Python
addDevice(deviceId, name, description, activateActivity=False)
``` 

creates a new device in the IOT platform.
if the device already exists, the function will fail
		return type : None

_parameters:_

- `deviceId:` The local identifier of the device
- `name:` the name of the device
- `description:` a description
- `activateActivity:` When true, historical data will be recorded for this device.
<type>type activateActivity:</type> bool


_returns_ True if the operation was succesful, otherwise False 

### addDeviceFromTemplate 

```Python
addDeviceFromTemplate(deviceId, templateId, values)
``` 

add a device to the cloud by using a predefined template that is stored in the cloud
<type>type deviceId:</type> string or int

_parameters:_

- deviceId:
- `templateId:` the id of the template that should be used
<type>type templateId:</type> basestring
- `values:` any optional values that have to be replaced in the template. This is specified as a
dictionary with key-value pairs.
<type>type values:</type> dictionary (json object)


_returns_: the definition of the device that was created (json/dictionary) or None if the template was not found 

### addGatewayAsset 

```Python
addGatewayAsset(id, name, description, isActuator, assetType, style='Undefined')
``` 

add an asset to the gateway 

### authenticate 

```Python
authenticate()
``` 

validate that the currently stored credentials are ok.


_returns_ True if succesful, otherwise False 

### connect 

```Python
connect(httpServer='api.AllThingsTalk.io', secure=False, certFile=None)
``` 

Create a connection with the http server

_parameters:_

- `httpServer:` The dns name of the server to use for HTTP communication
<type>type httpServer:</type> basestring
- `secure:` When true, an SSL connection will be used, if available. 

### createGateway 

```Python
createGateway(name, uid, assets=None)
``` 

Create a new orphan gateway in the cloud. After the gateway has been created, the user should claim it from within the website so that the gateway is assigned to the correct user account.  To finish the claim procedure, the gateway application should call 'finishclaim' after creating the gateway in the cloud.
When the gateway has ben succesfully created, use 'authenticate' to verify that the gateway still exists in the cloud whenever the gateway restarts.

_parameters:_

- `name:` the name ofhte gateway.
- `uid:` a globally unique id for gateways (ex: mac address)
- `assets:` a json structure with all the assets that should be created for the gateway. Default is None
See the [api documentation](http://docs-dev.AllThingsTalk.io/reference/devices/#-create-or-update-asset-) for more info.


_returns_: True when succesfull. 

### deleteAsset 

```Python
deleteAsset(device, id)
``` 

Delete the asset on the cloud with the specified name on the specified device.

_parameters:_

- `device:` the local name of the device.
- `id:` the local name of the asset


_returns_: True when the operation was successful (returned 204), otherwise False 

### deleteDevice 

```Python
deleteDevice(deviceId)
``` 

Deletes the specified device from the cloud.

_parameters:_

- `deviceId:` the local name of the device.


_returns_ true when successful. 

### deleteGatewayAsset 

```Python
deleteGatewayAsset(id)
``` 

Delete the asset on the cloud with the specified name on the specified device.

_parameters:_

- `device:` the local name of the device.
- `id:` the local name of the asset


_returns_: True when the operation was successful (returned 204), otherwise False 

### deviceExists 

```Python
deviceExists(deviceId)
``` 

checks if the device already exists in the IOT platform.

_parameters:_

- `deviceId:` the local name of the device.


_returns_ True when it already exists, otherwise False 

### finishclaim 

```Python
finishclaim(name, uid)
``` 

finish the claiming process for a previously created gateway.  When done, the system will store the credentials
return true if succesful, otherwise false 

### getAssetState 

```Python
getAssetState(assetId, deviceId)
``` 

look up the current state value for the asset with the specified local id, on the specified device (local id)


_returns_ json object. If not found, returns None 

### getGateway 

```Python
getGateway(includeDevices=True)
``` 



### send 

```Python
send(value, deviceId, assetId)
``` 

send the data to the cloud. Data can be a single value or object

_parameters:_

- `value:` the value to send in the form of a string. So a boolean is sent as 'true' or 'false', an integer can be sent as '1' and a fload as '  1.1'.  You can also send an object or a python list with this function to the cloud. Objects will be converted to json objects, lists become json arrays. The fields/records in the json objects or arrays must be the same as defined in the profile.
<type>type value:</type> string or json object
- `deviceId:` The local name of the device
- `assetId:` the local name of the asset 

### sendCommand 

```Python
sendCommand(value, gatewayId, deviceId, assetId)
``` 

send the data to the cloud. Data can be a single value or object

_parameters:_

- `value:` the value to send in the form of a string. So a boolean is sent as 'true' or 'false', an integer can be sent as '1' and a fload as '  1.1'.  You can also send an object or a python list with this function to the cloud. Objects will be converted to json objects, lists become json arrays. The fields/records in the json objects or arrays must be the same as defined in the profile.
<type>type value:</type> string or json object
- `deviceId:` The local name of the device
- `assetId:` the local name of the asset 

### sendValueHTTP 

```Python
sendValueHTTP(value, deviceId, assetId)
``` 

Sends a new value for an asset over http. This function is similar to send, accept that the latter uses mqtt
while this function uses HTTP

Parameters are the same as for the send function. 

### subscribe 

```Python
subscribe(mqttServer='broker.AllThingsTalk.io', port=1883, secure=False, certFile='cacert.pem')
``` 

start the mqtt client and make certain that it can receive data from the IOT platform

_parameters:_

- `mqttServer:`  the address of the mqtt server. Only supply this value if you want to a none standard server. Default = broker.AllThingsTalk.io
- `port:` the port number to communicate on with the mqtt server. Default = 1883
- `secure:` When true, an SSL connection is used. Default = False.  When True, use port 8883 on broker.AllThingsTalk.io
- `certFile:` certfile is a string pointing to the PEM encoded client
certificate and private keys respectively. Note
that if either of these files in encrypted and needs a password to
decrypt it, Python will ask for the password at the command line. It is
not currently possible to define a callback to provide the password.
Note: SSL will can only be used when the mqtt lib has been compiled with support for ssl 

