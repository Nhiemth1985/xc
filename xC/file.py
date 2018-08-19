"""
device_properties.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2018-08-14
        * Version: 0.03b
        * Added: Support to YAML files.

2018-07-18
        * Version: 0.02b
        * Added: Support to G-code files.

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
import yaml


class File:
    def __init__(self):
        self.version = '0.03b'
        self.reset()

    def reset(self):
        self.data = None

    def load(self, file, type):
        infoln('File: ' + str(file), 1)
        # Open file
        if not file:
            erroln('File definition missing.')
            sys.exit(True)
        try:
            f = open(file, 'r')
        except IOError as err:
            infoln('Failed.')
            erroln(str(err))
            sys.exit(True)
        # Set file type and format
        if type == 'json':
            data = f.read()
            self.json_load(data)
            self.json_check()
            self.json_info()
        elif type == 'gcode':
            data = f.readlines()
            self.gcode_load(data)
            self.gcode_check()
            self.gcode_info()
        elif type == 'yaml':
            data = f.read()
            self.yaml_load(data)
            self.yaml_check()
            self.yaml_info()
        f.close()

    def get(self):
        return self.data

    def yaml_load(self, data):
        self.reset()
        infoln('Parsing YAML...', 1)
        try:
            self.data = yaml.load(data)
        except ValueError as err:
            erroln(str(err))
            sys.exit(True)

    def yaml_check(self):
        self.items = len(self.data)

    def yaml_info(self):
        infoln('Keys: ' + str(self.items), 2)

    def gcode_load(self, data):
        self.reset()
        infoln('Parsing G-code...', 1)
        self.data = data

    def gcode_check(self):
        self.line_total = len(self.data)
        self.char_total = len(''.join(self.data))

    def gcode_info(self):
        infoln('Lines: ' + str(self.line_total), 2)
        infoln('Characters: ' + str(self.char_total), 2)

    def json_load(self, data):
        self.reset()
        infoln('Parsing JSON...', 1)
        try:
            self.data = json.loads(data)
        except ValueError as err:
            erroln(str(err))
            sys.exit(True)

    def json_info(self):
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
        infoln('Devices: ' + str(devices), 2)
        infoln('Hosts: ' + str(hosts), 2)

    def json_check(self):
        pass
