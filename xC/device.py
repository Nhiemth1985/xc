"""
device_properties.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2018-04-02
        * Version: 0.10b
        * Changed: Only configured interfaces are shown.

2018-02-11
        * Version: 0.09b
        * New feature: Added is_enable method.

2017-06-06
        * Version: 0.08b
        * New feature: Terminal line feed and carriage return customization.
        * New feature: Terminal local echo customization.

2017-06-06
        * Version: 0.07b
        * Improvement: Removed Warning messages.

2017-05-11
        * Version: 0.06b
        * New feature: Added startup() method.

2017-05-08
        * Version: 0.05b
        * New feature: Added presentation() method.

2017-04-01
        * Version: 0.04b
        * Improvement: Added version information.

2017-02-22
        * Version: 0.03b
        * Improvement: Removed method DeviceProperties.items_extended().
        * New feature: Added method DeviceProperties.is_network_connected().

2017-02-21
        * Version: 0.02b
        * Improvement: Added information messages.
        * Improvement: Added verbose error messages.

2017-02-20
        * Version: 0.01b
        * Improvement: Changed except ',' to 'as' to addopt Python 3 style.

2016-05-12
        * Version: 0.00b
        * Scrach version.
"""

import sys
import json
import os
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln


class DeviceProperties:
    """
    Methods:
    """
    def __init__(self, data):
        self.version = '0.10b'
        self.load(data)
        self.reset()

    def load(self, data):
        self.data = data

    def is_enable(self):
        enable = False
        try:
            enable = self.data[self.id].get('enable', True)
        except BaseException:
            pass
        return enable

    def get_id(self):
        return self.data[self.id]

    def set(self, id):
        """Set a device to be used.

        Used to set a device and import all elements.

        Attributes:
            element: An element name (like x1, x2, x6, etc.).
        """
        self.reset()
        if not id:
            return
        self.id = id
        # Is device present in configuration file?
        try:
            check_id = self.data[id]
        except KeyError:
            erroln('Device is not present in configuration file.')
            sys.exit(True)
        # Check mandatory keys.
        try:
            self.system_plat = self.data[id]["system"]["plat"]
            self.system_mark = self.data[id]["system"]["mark"]
            self.system_desc = self.data[id]["system"]["desc"]
            self.system_arch = self.data[id]["system"]["arch"]
            self.system_path = self.data[id]["system"]['path']
            self.system_logs = self.data[id]["system"]['logs']
        except KeyError as err:
            erroln('Mandatory key is absent: %s' % (err))
            sys.exit(True)

    def list(self):
        """Fetches device IDs from a dictionary.

        Args:
            None

        Returns:
            A list of device IDs. For example:

            ['x1', 'x2', 'x3', 'x4']

        Raises:
            None
        """
        elements = []
        for i in self.data:
            elements.append(i)
        elements.sort()
        return elements

    def get_comm(self):
        try:
            return self.data[self.id]["comm"]
        except BaseException:
            return []

    def get_objects(self):
        try:
            return self.data[self.id]["object"]
        except BaseException:
            return []

    def get_endup(self):
        try:
            return self.data[self.id]["endup"]
        except BaseException:
            return []

    def get_startup(self):
        try:
            return self.data[self.id]["startup"]
        except BaseException:
            return []

    def get_endup(self):
        try:
            return self.data[self.id]["endup"]
        except BaseException:
            return []

    def get_control(self):
        try:
            return self.data[self.id]["control"]
        except BaseException:
            return []

    def reset(self):
        """Reset device default properties"""
        self.id = None
        self.system_plat = ""
        self.system_mark = ""
        self.system_desc = ""
        self.system_arch = ""
        self.system_path = ""
        self.system_logs = ""

    def set_interface(self, interface):
        self.interface = interface

    def info(self):
        """ """
        infoln('Device...')
        infoln('ID: ' + str(self.id), 1)
        if not self.id:
            return
        infoln('Name: ' + str(self.system_plat) +
               ' Mark ' + str(self.system_mark), 1)
        infoln('Description: ' + str(self.system_desc), 1)
        # infoln('    Connectivity:')
        # if self.comm_serial_path is not None:
            # infoln('        Serial: ' + str(self.comm_serial_path))
            # infoln('        Speed: ' + str(self.comm_serial_speed) + ' bps')
        # if self.comm_network_address is not None:
            # infoln('        Network: ' + str(self.comm_network_address))

    def get_control_map(self):
        for i in self.objects():
            info(i)["command"]
