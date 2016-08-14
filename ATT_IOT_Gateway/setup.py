from setuptools import *

setup(
    name='att_iot_gateway',
    version='0.4.1',
    packages=find_packages(exclude=['pip', 'setuptools']),      # pip and setup tools are loaded in the virtual environment for the IDE.
    install_requires='paho-mqtt',
    url='https://github.com/allthingstalk/rpi-python-gateway-client',
    license='MIT',
    author='Jan Bogaerts',
    author_email='jb@allthingstalk.com',
	keywords = ['ATT', 'iot', 'internet of things', 'AllThingsTalk'],
    description='This package provides device & asset management + data feed features for the AllThingsTalk platform to your application.'
)
