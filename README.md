raspberrypi-python-client
==========

libraries that provide access to the ATT IOT platform, for the Python language (geared for gateway development).

Check the [api docs](#library.md) for more info.


### Installation
_with pip_
- install dependencies:
	sudo pip install paho-mqtt
- install lib
	sudo pip install att_iot_gateway

_manually_
- Run `git clone https://github.com/allthingstalk/rpi-python-gateway-client`
- Run `sudo bash rpi-python-gateway-client/setupNoShield.sh`

### Instructions

  1. Setup the hardware
  2. Open the 'xbee_gateway_demo.py' template script: `sudo nano xbee_gateway_demo.py`
  3. fill in the missing strings: replace clientId, clientKey. 
  4. Run the script: `python xbee_gateway_demo.py`
