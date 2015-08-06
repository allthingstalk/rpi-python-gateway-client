## globals
1. on_message: the callback function that will be called whenever data is sent from the IOT platform to one of the assets on your device.

Optional:
The following global variables are also needed for the system, but can be supplied by the platform.  You don't have to supply them manually. See the xbee example for more info.
2. CientId: the account id. This identifies you as the owner of the device.
3. ClientKey: the key that accompanies your account. It is used as a security token for http calls.
4. GatewayId: the id of the gateway.


## functions
`def connect(httpServer="beta.smartliving.io"):`

connect with the http server. This should be the firs call you do before creating any assets.

_parameters:_

1. httpServer: (string) optional, the name of the http server to connect to.

`def createGateway(name, uid, assets = None):`

Create a new orphan gateway in the cloud. After the gateway has been created, the user should claim it from within the website so that the gateway is assigned to the correct user account.  To finish the claim procedure, the gateway application should call 'finishclaim' after creating the gateway in the cloud.  
When the gateway has ben succesfully created, use 'authenticate' to verify that the gateway still exists in the cloud whenever the gateway restarts.

_parameters:_

1. name: (string) The name of the gateway.
2. uid: (string) a unique identifier for the gateway. This will become the code that the user must enter in order to 'claim' the gateway.  This value has to be unique within the system, otherwise the gateway will not be created.  Most often, the mac address of the gateway is used for this value.
3. assets: (optional, array): an optional array of assets that should be created for the gateway. The contents of this array should be asset objects. See the [api documentation](http://docs-dev.smartliving.io/reference/devices/#-create-or-update-asset-) for more info.

`def getGateway(includeDevices = True):`

Gets the details of the gateway that the library is currently serving for. In other words, the details will be returned of the gateway with the id specified in the global 'GatewayId'.

_parameters:_

1. includeDevices: (bool) optional, when true, alll the assets will also be included in the result. Otherwise, no asset details will be included.

`def finishclaim(name, uid):`

Finishes the claiming procedure.

_parameters:_

1. name: (string) The name of the gateway.
2. uid: (string) The same unique identifier that was used for creating the gateway.

`def authenticate():`

When the gateway has ben succesfully created, use 'authenticate' to verify that the gateway still exists in the cloud whenever the gateway restarts.  
Without authentication, the gateway will not be able to communicate with the cloud.


`def addDevice(deviceId, name, description):`

Creates a new device in the IOT platform. The deviceId is local to the gateway and should be unique within this context. Often, the mac address of the device is used. This function will fail if the device already exists. Use 'DeviceExists' to check if the device needs to be created or not.

_parameters:_

1. deviceId: (string) the id of the device that should be created. This has to be a unique value within the context of the gateway. 
2. name: (string) the name that the device should have. This is a free form string.
3. description: (string) a possible description of the device.

returns _True_ if the operation was successful, otherwise it returns _False_.

`def deviceExists(deviceId):`

Checks if the device already exists in the IOT platform. If it doesn't exist, you can create it with the function 'addDevice'.

_parameters:_

1. deviceId: (string) the id of the device that should be created. This should be a unique value within the IOT platform.

returns _True_ if the device already exists, otherwise _False_.

`def addAsset(id, deviceId, name, description, isActuator, assetType):`

create or update the specified asset. 

_parameters:_

1. id: (string) the local id of the asset. For instance '1', or '2'. Each asset should have a unique id within your script.
2. deviceId: (string) the id of the device that should be created. This should be a unique value within the context of the gateway. 
3. name: (string) the name that the asset should have. This is a free form string.
4. description: (string) a possible description of the asset.
5. isActuator: (bool) _True_ if it is possible to send values from the IOT platform to the asset. Use _False_ if it can only measure values and send them to the cloud. Note: actuators can also send values from the device to the IOT platform.
6. type: (string) The value type that the asset works with. Possible values can be: 'integer', 'double', 'boolean', 'dateTime', 'timeStamp', 'string'. Optionally, you can also specify the full [profile](http://docs-dev.smartliving.io/about/profiles/) type.

`def subscribe(mqttServer = "broker.smartliving.io", port = 1883):`

Sets up everything for the pub-sub client: create the connection, provide the credentials and register for any possible incoming data.

_parameters:_

1. mqttServer : (string) Optional, the name of the server to connect to.
2. port: (int) Optional, the port number of the server to connect to.

`def send(value, deviceId, assetId):`

send a data value to the cloud server for the device and asset with the specified id.

_parameters:_

1. value: (string or object) the value to send in the form of a string. So a boolean is sent as 'true' or 'false', an integer can be sent as '1' and a fload as '1.1'.  
You can also send an object or a python list with this function to the cloud. Objects will be converted to json objects, lists become json arrays. The fields/records in the json objects or arrays must be the same as defined in the profile.
2. deviceId: (string) the id of the device that contains the asset you want to send a value for. 
3. assetId: (string) the id of the asset to send the value to. This is the local id that you used while creating/updating the asset through the function 'AddAsset' Ex: '1'.

`def getAssetState(assetId, deviceId):`

Returns the last recorded value for the specified asset.  If no data has been recorded yet for the asset, the function will return 'None'.

_parameters:_

1. assetId: (string) the id of the asset to get the value for. This is the local id that you used while creating/updating the asset through the function 'AddAsset' Ex: '1'.
2. deviceId: (string) the id of the device that contains the asset you want to get a value for. 