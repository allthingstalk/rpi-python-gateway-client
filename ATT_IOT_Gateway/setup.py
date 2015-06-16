from setuptools import *

setup(
    name='att_iot_gateway',
    version='1.0.1.dev1',
    packages=find_packages(exclude=['pip', 'setuptools']),      # pip and setup tools are loaded in the virtual environment for the IDE.
    url='https://github.com/allthingstalk/rpi-python-gateway-client',
    license='MIT',
    author='Jan Bogaerts',
    author_email='jb@allthingstalk.com',
    description='This package provides device & asset management + data feed features for the AllThingsTalk platform to your application.'
)
