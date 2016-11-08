from distutils.core import setup

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

setup(
    name='att_iot_gateway',
    version='1.0.0',
    packages=['att_iot_gateway'],      # pip and setup tools are loaded in the virtual environment for the IDE.
    install_requires='paho-mqtt',
    url='https://github.com/allthingstalk/rpi-python-gateway-client',
    license='Apache Software License',
    author='Jan Bogaerts',
    author_email='jb@allthingstalk.com',
	keywords = ['ATT', 'iot', 'internet of things', 'AllThingsTalk'],
    description='This package provides device & asset management + data feed features for the AllThingsTalk platform to your application.'
)
