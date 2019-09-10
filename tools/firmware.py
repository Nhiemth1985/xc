"""
name: firmware.py
description: Device firmeware management package
copyright: 2016-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  contributors:
  - name: None
change-log:
  2019-03-05
  - version: 0.1
    fixed: pylint friendly
  2019-03-05
  - version: 0.09
    added: Verify (pylint3) support to MicroPython devices.
  2019-03-04
  - version: 0.08
    added: Upload support to MicroPython devices.
  2019-01-08
  - version: 0.07
    changed: Load minicom package directly.
  2018-11-16
  - version: 0.06b
    changed: os.system to subprocess OS command calls.
  2017-11-11
  - version: 0.05b
    added: Terminal line feed and carriage return customization.
    added: Terminal local echo customization.
  2017-06-04
  - version: 0.04b
    fixed: fixed program execution check.
  2017-05-08
  - version: 0.03b
    fixed: Removed '\n' character from self.device_path for serial
  devices.
  2017-04-01
  - version: 0.02b
    Improvement: added version information.
  2017-02-24
  - version: 0.01b
    added: Check program before execution
    added: Checks for arduino and miniterm.py executables on system.
  2016-02-13
  - version: 0.00b
    Scrach version.
"""

import sys
import os.path
import subprocess
from serial.tools.miniterm import Miniterm
from tools.session import Session
import tools.echo as echo


class DevTools:  # pylint: disable=too-many-instance-attributes
    """
    description:
    """

    def __init__(self, data):
        self._version = 0.1
        self.arduino_program = "arduino"
        self.__id = None
        self.platform = None
        self.mark = None
        self.description = None
        self.architecture = None
        self.system_path = None
        self.system_work = None
        self.system_code = None
        self.system_logs = None
        self.path = None
        self.arduino_file = None
        self.logs = None
        self.device_path = None
        self.device_speed = None
        self.terminal_echo = False
        self.terminal_end_of_line = 'LF'
        self.network_address = None
        self.device_port = None
        self.interface = 'serial'
        self.destination = ''
        self.load(data)
        self.__set()

    def __set(self):
        self.__id = None
        self.platform = self.data["system"].get("plat", self.platform)
        self.mark = self.data["system"].get("mark", self.mark)
        self.description = self.data["system"].get("desc", self.description)
        self.architecture = self.data["system"].get("arch", self.architecture)
        self.system_path = self.data["system"].get("path", self.system_path)
        self.path = os.path.join(os.environ['HOME'], self.system_path)
        self.arduino_file = self.path[self.path.rfind("/", 0):] + ".ino"
        self.system_work = self.data["system"].get("work", self.system_work)
        self.system_work = os.path.join(os.environ['HOME'], self.system_work)
        self.system_code = self.data["system"].get("code", self.system_code)
        self.system_logs = self.data["system"].get("logs", self.system_logs)
        self.logs = os.path.join(os.environ['HOME'], self.system_logs)
        self.device_path = self.data["comm"]["serial"]\
            .get("path", self.device_path)
        self.device_speed = self.data["comm"]["serial"]\
            .get("speed", self.device_speed)
        self.terminal_echo = self.data["comm"]["serial"]\
            .get("terminal_echo", self.terminal_echo)
        self.terminal_end_of_line = self.data["comm"]["serial"]\
            .get("terminal_end_of_line", self.terminal_end_of_line)
        self.network_address = self.data["comm"]\
            .get("arch", self.network_address)
        self.device_port = self.data["comm"].get("arch", self.device_port)
        self.interface = 'serial'
        if self.interface == 'serial':
            self.destination = os.popen("echo -n $(readlink -f " +
                                        self.device_path + ")").read().rstrip()
        elif self.interface == 'network':
            self.destination = self.network_address

    def load(self, data):
        """
        description:
        """
        self.data = data

    def info(self):
        """
        description:
        """
        echo.infoln('Project...')
        echo.infoln('    Platform: ' + self.platform)
        echo.infoln('    Architecture: ' + self.architecture)

    # def reset(self):
        # """
        # description:
        # """
        # self.__id = None
        # self.platform = None
        # self.mark = None
        # self.description = None
        # self.architecture = None
        # self.system_path = None
        # self.system_work = None
        # self.system_code = None
        # self.system_logs = None
        # self.path = None
        # self.arduino_file = None
        # self.logs = None
        # self.device_path = None
        # self.device_speed = None
        # self.terminal_echo = False
        # self.terminal_end_of_line = 'LF'
        # self.network_address = None
        # self.device_port = None
        # self.interface = 'serial'
        # self.destination = ''

    def terminal(self):
        """
        description:
        """
        # Connect a terminal to SSH console.
        if 'linux' in self.architecture:
            ret = os.system('ssh' + ' ' + 'xc' + '@' + self.network_address)
            if ret != 0:
                echo.erroln("Return code: " + str(ret))
            sys.exit(ret)
        # Connect a terminal to SSH console.
        if self.interface == 'network':
            ret = os.system('ssh' + ' ' + 'root' + '@' +
                            str(self.network_address) +
                            ' telnet localhost 6571')
            if ret != 0:
                echo.erroln("Return code: " + str(ret))
            sys.exit(ret)
        # Connect a terminal to device serial console.
        echo.infoln("Communication device: " +
                    os.popen("readlink -f " + self.device_path).read().rstrip())
        # Start serial session
        session = Session(self.data["comm"])
        instance = session.start()
        if instance is True:
            sys.exit(True)
        # Start minicom session
        miniterm = Miniterm(instance,
                            echo=self.terminal_echo,
                            eol=self.terminal_end_of_line.lower(),
                            filters=[])
        miniterm.exit_character = chr(0x1d)
        miniterm.menu_character = chr(0x14)
        miniterm.raw = True
        miniterm.set_rx_encoding('UTF-8')
        miniterm.set_tx_encoding('UTF-8')
        miniterm.start()
        try:
            miniterm.join(True)
        except KeyboardInterrupt:
            pass
        miniterm.join()
        miniterm.close()
        sys.exit(False)

    def verify(self):
        """
        description:
        """
        echo.infoln('Verifying...')
        # MicroPython
        if self.architecture == "MicroPython:ARM:PYBv1.1":
            cmd = 'find ' + self.system_work + ' -name "*.py" ' + \
                  '-exec pylint3 {} \;'  # pylint: disable=anomalous-backslash-in-string
        # arduino
        else:
            # Check if arduino exists
            if __which(self.arduino_program) is None:
                echo.erroln('Program not found: ' + self.arduino_program)
                sys.exit(True)
            # Build command
            cmd = self.arduino_program + \
                " --verify --board " + self.architecture + " " + \
                self.path + "/" + self.arduino_file
        if echo.level() < 3:
            cmd += " >/dev/null 2>&1"
        return_code = subprocess.call(cmd, shell=True)
        if return_code != 0:
            echo.erroln("Return code: " + str(return_code))
            if return_code > 127:
                return_code = 1
        echo.infoln('')
        sys.exit(return_code)

    def upload(self):
        """
        description:
        """
        echo.infoln('Uploading...')
        # MicroPython
        if self.architecture == "MicroPython:ARM:PYBv1.1":
            cmd = 'rsync \
                   --archive --delete --verbose --compress \
                   --exclude "*.md" \
                   --exclude "*.gnbs.conf" \
                   --exclude ".rsyncignore" \
                   --exclude "Pictures" \
                   ' + self.system_work + '/* ' + self.system_code + '/' + \
                   "; sync"
            echo.infoln("From: " + self.system_work, 1)
            echo.infoln("To: " + self.system_code, 1)
        # Arduino
        else:
            # Check if arduino program exists
            if __which(self.arduino_program) is None:
                echo.erroln('Program not found: ' + self.arduino_program)
                sys.exit(True)
            # Build command
            cmd = self.arduino_program + " --upload --board " + \
                self.architecture + " " + \
                self.path + "/" + self.arduino_file + \
                " --port " + self.destination
            echo.infoln("Communication device: " + self.destination.rstrip() + ".")
        if echo.level() < 3:
            cmd += " >/dev/null 2>&1"
        return_code = subprocess.call(cmd, shell=True)
        if return_code == 0:
            file_obj = open(self.logs + "/.buildno", 'r')
            buildno = file_obj.read()
            file_obj.close()
            if buildno == "":
                buildno = 1
            else:
                buildno = int(buildno) + 1
            file_obj = open(self.logs + "/.buildno", 'w')
            file_obj.write(str(buildno))
            echo.infoln("Build number: " + str(buildno))
        else:
            echo.erroln("Return code: " + str(return_code))
            if return_code > 127:
                return_code = 1
        echo.infoln('')
        sys.exit(return_code)


def __which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath = os.path.split(program)[0]
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None
