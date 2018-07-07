"""
session.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2016-02-19
        * Version: 0.01b
        * Scrach version.
"""

import os.path
import os
from serial import Serial
import sh
from socket import gethostbyname
import sys
from time import sleep
from xC.timer import Timer
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln


class Session:
    def __init__(self, data):
        self.version = '0.01b'
        self.reset()
        self.load(data)

    def reset(self):
        self.comm_serial_path = ""
        self.comm_serial_speed = 0
        self.comm_serial_terminal_echo = True
        self.comm_serial_terminal_end_of_line = "CRLF"
        self.comm_serial_delay = 0
        self.comm_network_address = None

    def load(self, data):
        self.data = data
        if self.data == []:
            self.data = None
            return
        try:
            self.comm_serial_path = self.data["serial"]\
                .get('path', self.comm_serial_path)
            self.comm_serial_speed = self.data["serial"]\
                .get('speed', self.comm_serial_speed)
            self.comm_serial_delay = self.data["serial"]\
                .get('delay', self.comm_serial_delay)
            self.comm_serial_terminal_echo = self.data["serial"]\
                .get('terminal_echo', self.comm_serial_terminal_echo)
            self.comm_serial_terminal_end_of_line = \
                self.data["serial"]\
                .get('terminal_end_of_line',
                     self.comm_serial_terminal_end_of_line)
            self.comm_network_address = (
                self.data["network"].get('address', self.comm_network_address))
        except KeyError as err:
            pass

        # Get IP address from host name
        try:
            self.comm_network_address = gethostbyname(self.comm_network_address)
        except BaseException:
            pass
        return 0

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
            if self.is_connected_serial():
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

    def is_connected(self):
        if self.is_connected_serial() or self.is_connected_network():
            return True

    def is_connected_serial(self):
        return os.path.exists(self.comm_serial_path)

    def is_connected_network(self):
        if self.comm_network_address is None:
            return False
        try:
            sh.ping(self.comm_network_address, '-c 2 -W 1', _out='/dev/null')
            return True
        except BaseException:
            return False

    def stop(self):
        pass

    def select_auto(self):
        self.id = self.detect()
        if self.id:
            self.select(self.id)
        return self.id

    def start(self):
        if not self.data:
            return
        infoln("Connecting...", 1)
        if self.is_connected_serial():
            try:
                sleep(self.comm_serial_delay / 1000)
                self.session = Serial(self.comm_serial_path,
                                      self.comm_serial_speed,
                                      timeout=1)
            except BaseException:
                return True
            return self.session
        else:
            warnln('Device is not connected.', '        ')
            return True

    def info(self):
        infoln('Session...')
        if not self.data:
            return
        if self.comm_serial_path is not None:
            infoln('    Serial: ' + str(self.comm_serial_path))
            infoln('    Speed: ' + str(self.comm_serial_speed) + ' bps')
        if self.comm_network_address is not None:
            infoln('    Network: ' + str(self.comm_network_address))
