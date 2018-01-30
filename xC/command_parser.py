"""
commandparser.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
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

import re
import sys
from time import sleep
# import spur
from xC.timer import Timer
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln


class CommandParser:
    """
    """
    def __init__(self, connection):
        self.version = '0.04b'
        self.connection = connection
        self.retry = 3  # times
        self.timeout = 100  # milliseconds

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
            received = self.connection.readline().rstrip()
        except IOError as err:
            return True
        if received == "" or received == "\n" or received == "\r":
            return False
        # Change color based on device response ('ok' or 'nok')
        if re.search('nok', str(received)):
            color = 'red'
        else:
            color = 'green'
        # Display device response
        codeln(received, color)
        return received

    def send(self, command):
        """Just send a message"""
        # Store comments
        try:
            comment = command[re.search(';', command).span()[0]:]
        except:
            comment = ''
        if comment == '':
            try:
                comment = command[re.search('\(', command).span()[0]:]
            except:
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
            self.connection.write((command + '\n').encode())
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
        while True:
            if self.receive() == "":
                return 0

    def load(self, gcode_file):
        """Load and parse G-Code file.

        Args:
            file: Absolute path to G-Code file.

        Returns:
            0: OK
            1: Error (file not found or access denied)

        Raises:
            IOError: An error occurred accessing the bigtable.Table object.
        """
        # Open program file
        infoln('Loading program file...')
        if gcode_file is None or gcode_file == '':
            erroln('Please define G-code program file.')
            sys.exit(True)
        try:
            f = open(gcode_file)
            self.gcode = f.readlines()
            f.close()
        except IOError as err:
            # erroln(str(err))
            return True
        return False

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
