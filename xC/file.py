"""
device_properties.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2018-07-04
        * Version: 0.02b
        * Added:

2018-06-29
        * Version: 0.01b
        * Added: Support to JSON files.

"""

import sys
import json
import os
from socket import gethostbyname
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln


class FileManagement:
    def __init__(self, config):
        self.version = '0.01b'
        self.check()
        self.load(config)
        self.info()

    def load(self, config):
        self.config = config
        # Open JSON configuration file
        infoln('Loading configuration...')
        try:
            infoln('File: ' + self.config, 1)
            f = open(self.config).read()
        except IOError as err:
            infoln('Failed.')
            erroln(str(err))
            sys.exit(True)
        # Import JSON data
        infoln('Parsing JSON...')
        try:
            self.data = json.loads(f)
        except ValueError as err:
            infoln('Failed')
            erroln(str(err))
            infoln('Ops... there\'s something strange in your neighborhood.')
            sys.exit(True)
        return False

    def get(self):
        return self.data

    def info(self):
        hosts = 0
        devices = 0
        try:
            hosts = len(self.data["host"])
        except BaseException:
            pass
        try:
            devices = len(self.data["device"])
        except BaseException:
            pass
        infoln('Hosts: ' + str(hosts), 1)
        infoln('Devices: ' + str(devices), 1)

    def check(self):
        pass
