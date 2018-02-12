"""
deviceproperties.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
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

import json
import os
import sh
from socket import gethostbyname
import sys
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln


class DeviceProperties:
    """
    Methods:
    """
    def __init__(self, devices_file):
        self.version = '0.09b'
        self.devices_file = devices_file
        self.set()
        self.load(devices_file)

    def is_enable(self):
        enable = False
        try:
            enable = self.data["device"][self.id].get('enable', True)
        except:
            pass
        return enable

    def select(self, id):
        """Set a device to be used.

        Used to set a device and import all elements.

        Attributes:
            element: An element name (like x1, x2, x6, etc.).
        """
        self.reset()
        self.id = id
        # Is device present in configuration file?
        try:
            check_id = self.data["device"][id]
        except KeyError:
            erroln('Device is not present in configuration file.')
            sys.exit(True)
        # Check mandatory keys.
        try:
            self.system_plat = self.data["device"][id]["system"]["plat"]
            self.system_mark = self.data["device"][id]["system"]["mark"]
            self.system_desc = self.data["device"][id]["system"]["desc"]
            self.system_arch = self.data["device"][id]["system"]["arch"]
            self.system_path = self.data["device"][id]["system"]['path']
            self.system_logs = self.data["device"][id]["system"]['logs']
        except KeyError as err:
            erroln('Mandatory key is absent: %s' % (err))
            sys.exit(True)
        # Check secondary keys.
        try:
            self.comm_serial_path = self.data["device"][id]["comm"]["serial"]\
                .get('path', self.comm_serial_path)
            self.comm_serial_speed = self.data["device"][id]["comm"]["serial"]\
                .get('speed', self.comm_serial_speed)
            self.comm_terminal_echo = self.data["device"][id]["comm"]["serial"]\
                .get('terminal_echo', self.comm_terminal_echo)
            self.comm_terminal_end_of_line = \
                self.data["device"][id]["comm"]["serial"]\
                .get('terminal_end_of_line', self.comm_terminal_end_of_line)
            self.comm_network_address = (
                self.data["device"][id]["comm"]
                ["network"].get('address', self.comm_network_address))
        except KeyError as err:
            # warnln('Absent key: %s' % (err))
            pass
        # Get IP address from host name
        try:
            self.comm_network_address = gethostbyname(self.comm_network_address)
        except:
            pass
        return 0

    def select_auto(self):
        self.id = self.detect()
        if self.id:
            self.select(self.id)
        return self.id

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
        for i in self.data["device"]:
            elements.append(i)
        elements.sort()
        return elements

    def is_serial_connected(self):
        return os.path.exists(self.comm_serial_path)

    def is_network_connected(self):
        if self.comm_network_address is None:
            return False
        try:
            sh.ping(self.comm_network_address, '-c 2 -W 1', _out='/dev/null')
            return True
        except:
            return False

    def load(self, file):
        """Load and parse configuration.

        Args:
            file: Absolute path to JSON file.

        Returns:
            0: OK
            1: File error (file not found or access denied)
            2: Can't parse JSON data

        Raises:
            IOError: An error occurred accessing the bigtable.Table object.
        """
        # Open JSON devices file
        infoln('Loading configuration file...')
        try:
            f = open(file).read()
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

    def objects(self):
        try:
            return self.data["device"][self.id]["object"]
        except:
            return []

    def endup(self):
        try:
            return self.data["device"][self.id]["endup"]
        except:
            return []

    def startup(self):
        try:
            return self.data["device"][self.id]["startup"]
        except:
            return []

    def control(self):
        try:
            return self.data["device"][self.id]["control"]
        except:
            return []

    def reset(self):
        """Reset device default properties"""
        self.set()

    def set(self):
        """Set device default properties"""
        self.id = ""
        self.system_plat = ""
        self.system_mark = ""
        self.system_desc = ""
        self.system_arch = ""
        self.system_path = ""
        self.system_logs = ""
        self.comm_serial_path = ""
        self.comm_serial_speed = 0
        self.comm_terminal_echo = True
        self.comm_terminal_end_of_line = "CRLF"
        self.comm_network_address = None

    def detect(self):
        """

        Args:
            None.

        Returns:
            False: No device connected
            True: A list containing all connected devices ID.
            Str: a string containing a device ID.

        Raises:
            IOError: An error occurred accessing the bigtable.Table object.
        """
        ids = []
        for i in self.list():
            self.select(i)
            if self.is_serial_connected():
                ids.append(i)
        self.reset()
        if len(ids) == 1:
            self.id = ids[0]
            return self.id
        elif len(ids) > 1:
            erroln('Too much connected devices.')
            infoln('Use -h option and select just one of these devices:')
            for i in ids:
                infoln('  ' + str(i))
            sys.exit(True)
        elif len(ids) < 1:
            return False

    def presentation(self):
        """ """
        infoln('Device...')
        infoln('    ID: ' + str(self.id))
        infoln('    Project: ' + str(self.system_plat) +
               ' Mark ' + str(self.system_mark) +
               ' (' + str(self.system_desc) + ')')
        infoln('    Connectivity:')
        infoln('        Serial: ' + str(self.comm_serial_path) + ' (' +
               str(self.comm_serial_speed) + ' bps)')
        infoln('        Network: ' + str(self.comm_network_address))
