raspberrypi-python-client
==========

libraries that provide access to the ATT IOT platform, for the Python language (geared for RPI development).

Check the wiki pages for [how-to's & API documentation](https://github.com/allthingstalk/raspberrypi-python-client/wiki).

<!--

### flavours
There are 2 flavours of the IOT library. Use a library according to your needs.
  1. regular: The RPI will act as a single device, directly connected to the IOT platform. You are responsible for creating the device manually on the platform, any assets can be created through the script.
  2. gateway: The RPI will function as a gateway for other devices, which communicate with the gateway-RPI through xbee modules. Devices and their assets are automatically created whenever a new xbee device connects to the gateway.


### Dependencies
  1. The library depend on the [paho.mqtt.client module](http://eclipse.org/paho/clients/python/).
  


  2. the demo template script for the gateway also relies on:
    - [pyserial] (http://pyserial.sourceforge.net/)
	- [python-xbee] (https://code.google.com/p/python-xbee/)

-->

### Installation
- Run `git clone https://github.com/allthingstalk/rpi-python-gateway-client`
- Run `sudo bash rpi-python-gateway-client/setupNoShield.sh`

### Instructions

  1. Setup the hardware
  2. Open the 'xbee_gateway_demo.py' template script: `sudo nano xbee_gateway_demo.py`
  3. fill in the missing strings: replace deviceId, clientId, clientKey. Optionally change/add the sensor & actuator names, pins, descriptions, types. 
  4. Run the script: `python xbee_gateway_demo.py`