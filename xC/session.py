"""
session.py

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log:
2017-07-27
        * Version: 0.05b
        * New feature: Featured colours to 'ok' and 'nok' received strings.

2017-06-04
        * Version: 0.04b
        * New feature: Added comment parser to '()'

2017-06-02
        * Version: 0.03b
        * New feature: Added comment parser to ';'

2017-05-11
        * Version: 0.02b
        * New feature: Added is_ready() method.
        * Bug fix: Added new line to send and receive screen output.
        * Improvement: Added command string filter in send() method.

2017-02-21
        * Version: 0.01b
        * Improvement: Added information messages.

2016-02-19
        * Version: 0.00b
        * Scrach version.
"""

import os.path
import os
import re
from serial import Serial
# import sh
from socket import gethostbyname
import sys
from time import sleep
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln
from xC.timer import Timer


class Session:
    def __init__(self, data):
        self.version = '0.05b'
        self.reset()
        self.load(data)

    def reset(self):
        self.data = None
        self.comm_serial_path = ''
        self.comm_serial_speed = 0
        self.comm_serial_terminal_echo = True
        self.comm_serial_terminal_end_of_line = 'CRLF'
        self.comm_serial_delay = 0
        self.comm_network_address = None
        self.retry = 3  # times
        self.timeout = 100  # milliseconds

    def load(self, data):
        if data == []:
            return
        self.data = data
        # Optional keys
        try:
            self.comm_serial_path = self.data["serial"]\
                .get('path', self.comm_serial_path)
            self.comm_serial_speed = self.data["serial"]\
                .get('speed', self.comm_serial_speed)
            self.comm_serial_delay = self.data["serial"]\
                .get('delay', self.comm_serial_delay)
            self.comm_serial_terminal_echo = self.data["serial"]\
                .get('terminal_echo', self.comm_serial_terminal_echo)
            self.comm_serial_terminal_end_of_line = self.data["serial"]\
                .get('terminal_end_of_line',
                     self.comm_serial_terminal_end_of_line)
        except KeyError as err:
            pass
        # Network configuration
        try:
            self.comm_network_address = (
                self.data["network"].get('address', self.comm_network_address))
            # Get IP address from host name
            self.comm_network_address = gethostbyname(self.comm_network_address)
        except BaseException:
            pass
        return 0

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
        if self.session:
            self.session.close()
        self.reset()

    def start(self):
        if not self.data:
            return
        infoln("Connecting...", 1)
        if self.is_connected_serial():
            try:
                self.session = Serial(self.comm_serial_path,
                                      self.comm_serial_speed,
                                      timeout=1)
            except BaseException:
                warnln('Operation not completed.', 2)
                return False
            sleep(self.comm_serial_delay / 1000)
            infoln('Speed: ' + str(self.comm_serial_speed) + ' bps', 2)
            return self.session
        else:
            warnln('Device is not connected.', 2)
            return True

    def info(self):
        infoln('Session...')
        if not self.data:
            return
        if self.comm_serial_path is not None:
            infoln('Serial: ' + str(self.comm_serial_path), 1)
            infoln('Startup delay: ' + str(self.comm_serial_delay) + ' ms', 1)
        if self.comm_network_address is not None:
            infoln('Network: ' + str(self.comm_network_address), 1)

    def check_device(self):
        if not self.check_device_timer.check():
            return
        if (self.session.is_connected() is False) and \
           (self.session.is_ready() is True):
            self.id = None
            self.interface = 'serial'
            self.start()
        if self.session.is_connected() is False:
            if self.device.detect():
                self.start()

    def run(self):
        infoln('Running program...')
        go_on = False
        while not go_on:
            go_on = self.is_ready()
        lines = len(self.gcode)
        n = 0
        while True:
            if go_on:
                if n == lines:
                    break
                line = self.gcode[n]
                n += 1
                if self.send(line):
                    continue
            received = self.receive()
            m = re.search('ok', str(received))
            if m:
                go_on = True
            else:
                go_on = False

    def is_ready(self):
        i = 0
        while True:
            b = self.receive()
            if b is False:
                i += 1
            else:
                i = 0
            if i > 1:
                break
        return True

    def play(self):
        pass

    def pause(self):
        pass

    def send_expect(self, command, expected, timeout=0, retry=0):
        """Send a command and receive a message.

        Retrieves rows pertaining to the given keys from the Table
        instance represented by big_table.  Silly things may happen if
        other_silly_variable is not None.

        Args:
            command:
            expected:
                A list with three items:
                [0] Header
                    - Description: Field used to start a message.
                    - Default value: This is a required field.
                [1] Payload
                    - Description: Message content.
                                   Also kown as data field.
                    - Default value: This is a required field.
                [2] Trailer
                    - Description: Control field used to identify end of
                                   message.
                                   Also known as footer field.
                    - Default value: '\n'
            timeout:
            retry:

        Returns:
            A dict mapping keys to the corresponding table row data
            fetched. Each row is represented as a tuple of strings. For
            example:

            {'Serak': ('Rigel VII', 'Preparer'),
             'Zim': ('Irk', 'Invader'),
             'Lrrr': ('Omicron Persei 8', 'Emperor')}

            If a key from the keys argument is missing from the dictionary,
            then that row was not found in the table.

        Raises:
            IOError: An error occurred accessing the bigtable.Table object.
        """
        if retry == 0:
            retry = self.retry
        if timeout == 0:
            timeout = self.timeout
        try:
            self.send(command)
        except IOError as err:
            return True
        serial_line = ""
        for i in range(retry):
            sleep(int((timeout) / 1000))
            serial_line += self.receive()
            if expected in serial_line:
                return serial_line
        erro("Command return lost.")
        return True

    def receive(self):
        """Just receive a message"""
        try:
            received = self.session.readline().rstrip()
        except IOError as err:
            return True
        if received == "":  # or received == "\n" or received == "\r":
            return False
        # Change color based on device response ('ok' or 'nok')
        if re.search('nok', str(received)):
            codeln(received, 'red', attrs=['bold'])
            return received
        elif re.search('ok', str(received)):
            codeln(received, 'green', attrs=['bold'])
            return received
        else:
            codeln(received, 'green')
            return received

    def send(self, command):
        """Just send a message"""
        # Store comments
        try:
            comment = command[re.search(';', command).span()[0]:]
        except BaseException:
            comment = ''
        if comment == '':
            try:
                comment = command[re.search('\(', command).span()[0]:]
            except BaseException:
                comment = ''
        # Remove comments
        command = re.sub(r'(?:_a)?\(([^(]*)$', '\n', command)
        command = re.sub(r'(?:_a)?\;([^;]*)$', '\n', command)
        # Trim start and end spaces
        command = command.strip(' ').rstrip()
        comment = comment.strip(' ').rstrip()
        # Ignore blank lines
        if command == '':
            if comment != '':
                codeln(comment)
            return True
        code(command, attrs=['bold'])
        codeln('  ' + comment)
        try:
            self.session.write((command + '\n').encode())
        except IOError as err:
            return True
        return False

    def send_wait(self, command):
        self.send(command)
        while True:
            received = self.receive()
            if re.search('ok', str(received)):
                break

    def set_retry(self, retry):
        """Set default number of retries"""
        self.retry = retry

    def set_timeout(self, timeout):
        """Set default timeout value"""
        self.timeout = timeout

    def clear(self):
        """ Clear message buffer """
        while self.receive():
            continue

    def set_program(self, data):
        """Set G-Code.
        """
        if not data or data == '':
            erroln('Invalid G-code file.')
            sys.exit(True)
        self.gcode = data
