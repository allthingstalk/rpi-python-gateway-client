RPI-python-gateway-client
==========

A library that provide access to the ATT IOT platform, for the Python language. It allows you to run your device as a gateway for other devices, providing 2 way communication between HAN (home area network) devices and the internet.

Check the wiki pages for [how-to's & API documentation](https://github.com/allthingstalk/raspberrypi-python-client/wiki).


### Installation

**automatic**
- Run:
`pip install att_iot_gateway`

**Manual:**
- Run `git clone https://github.com/allthingstalk/rpi-python-gateway-client`
- Run `sudo bash rpi-python-gateway-client/setupNoShield.sh`

### Instructions

  1. Setup the hardware
  2. Open the 'xbee_gateway_demo.py' template script: `sudo nano xbee_gateway_demo.py` 
  4. Run the script: `python xbee_gateway_demo.py`
  5. Claim the gateway
