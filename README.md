raspberrypi-python-client
==========

libraries that provide access to the ATT IOT platform, for the Python language (geared for gateway development).

Check the [api docs](https://github.com/allthingstalk/rpi-python-gateway-client/blob/master/library.md) for more info.


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

1. Set up your xbee hardware
  2. Get the mac address of your RPI `ifconfig`
  2. Run the script: `python xbee_gateway_demo.py`
  3. Go to the website and 
  4. claim your gateway using the mac address from step 2  


