"""
---
name: file.py
description: File package
copyright: 2018-2019 Márcio Pessoa
people:
  developers:
  - name: Márcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
  2019-08-27
  - version: 0.6
    added: Minor upgrades.
  2019-07-08
  - version: 0.05
    fixed: Verboseless messages.
  2018-08-14
  - version: 0.03b
    added: Support to YAML files.
  2018-07-18
  - version: 0.02b
    added: Support to G-code files.
  2018-06-29
  - version: 0.01b
    added: Support to JSON files.
"""

import sys
import json
import yaml


class File:
    """
    description:
    """

    def __init__(self):
        self.version = 0.6
        self.data = None

    def load(self, file, kind):
        """
        description:
        """
        # debugln('File: ' + str(file), 1)
        # Open file
        if not file:
            # File definition missing
            sys.exit(True)
        try:
            f = open(file, 'r')
        except IOError as err:
            print(err)
            sys.exit(True)
        # Set file type and format
        if kind == 'json':
            data = f.read()
            self.json_load(data)
            self.json_info()
        elif kind == 'gcode':
            data = f.readlines()
            self.gcode_load(data)
            self.gcode_info()
        elif kind == 'yaml':
            data = f.read()
            self.yaml_load(data)
            self.yaml_info()
        f.close()

    def get(self):
        """
        description:
        """
        return self.data

    def yaml_load(self, data):
        """
        description:
        """
        # self.reset()
        # debugln('Parsing YAML...', 1)
        try:
            self.data = yaml.load(data)
        except ValueError as err:
            print(err)
            # erroln(str(err))
            sys.exit(True)

    def yaml_info(self):
        """
        description:
        """
        items = len(self.data)
        return {'items': items}

    def gcode_load(self, data):
        """
        description:
        """
        # self.reset()
        # debugln('Parsing G-code...', 1)
        self.data = data

    def gcode_info(self):
        """
        description:
        """
        line_total = len(self.data)
        char_total = len(''.join(self.data))
        return {'lines': line_total, 'chars': char_total}

    def json_load(self, data):
        """
        description:
        """
        # self.reset()
        # debugln('Parsing JSON...', 1)
        try:
            self.data = json.loads(data)
        except ValueError as err:
            print(err)
            # erroln(str(err))
            sys.exit(True)

    def json_info(self):
        """
        description:
        """
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
        return {'devices': devices, 'hosts': hosts}
