"""
devtools.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2017-11-11
        * Version: 0.05b
        * New feature: Terminal line feed and carriage return customization.
        * New feature: Terminal local echo customization.

2017-06-04
        * Version: 0.04b
        * Bug fix: Fixed program execution check.

2017-05-08
        * Version: 0.03b
        * Bug fix: Removed '\n' character from self.device_path for serial
          devices.

2017-04-01
        * Version: 0.02b
        * Improvement: Added version information.

2017-02-24
        * Version: 0.01b
        * Added check program before execution
          * Checks for arduino and miniterm.py executables on system.

2016-02-13
        * Version: 0.00b
        * Scrach version.
"""

import os.path
import sys
import time
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln


class DevTools:
    """docstring"""

    def __init__(self, data):
        """docstring"""
        self.version = '0.05b'
        self.terminal_program = "miniterm.py"
        self.arduino_program = "arduino"
        self.load(data)
        self.set()

    def load(self, data):
        self.data = data

    def info(self):
        infoln('Project...')
        infoln('    Platform: ' + self.platform)
        infoln('    Architecture: ' + self.architecture)

    def set(self):
        self.reset()
        self.id = id
        self.platform = self.data["system"].get("plat", self.platform)
        self.mark = self.data["system"].get("mark", self.mark)
        self.description = self.data["system"].get("desc", self.description)
        self.architecture = self.data["system"].get("arch", self.architecture)
        self.system_path = self.data["system"].get("path", self.system_path)
        self.path = os.path.join(os.environ['HOME'], self.system_path)
        self.arduino_file = self.path[self.path.rfind("/", 0):] + ".ino"
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
        self.network_address = self.data["comm"].get("arch",
                                                     self.network_address)
        self.device_port = self.data["comm"].get("arch", self.device_port)
        self.interface = 'serial'
        if self.interface == 'serial':
            self.destination = os.popen("echo -n $(readlink -f " +
                                        self.device_path + ")").read().rstrip()
        elif self.interface == 'network':
            self.destination = self.network_address

    def reset(self):
        self.id = None
        self.platform = None
        self.mark = None
        self.description = None
        self.architecture = None
        self.system_path = None
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

    def terminal(self):
        # Check if miniterm.py exists
        if self.__which(self.terminal_program) is None:
            erroln('Program not found: ' + self.terminal_program)
            sys.exit(True)
        # Connect a terminal to SSH console.
        if 'linux' in self.architecture:
            ret = os.system('ssh' + ' ' + 'xc' + '@' + self.network_address)
            if ret != 0:
                erroln("Return code: " + str(ret))
            sys.exit(ret)
        # Connect a terminal to SSH console.
        if self.interface == 'network':
            ret = os.system('ssh' + ' ' + 'root' + '@' +
                            str(self.network_address) +
                            ' telnet localhost 6571')
            if ret != 0:
                erroln("Return code: " + str(ret))
            sys.exit(ret)
        # Connect a terminal to device serial console.
        local_echo = ''
        if self.terminal_echo:
            local_echo = "--echo"
        infoln("Communication device: " +
               os.popen("readlink -f " + self.device_path).read())
        command = (self.terminal_program + " " +
                   self.device_path + " " +
                   str(self.device_speed) + " " +
                   "--eol " + self.terminal_end_of_line + " " +
                   local_echo + " " +
                   "--quiet")
        codeln(command)
        return_code = os.system(command)
        if return_code != 0:
            erroln("Return code: " + str(return_code))
            if return_code > 127:
                return_code = 1
        sys.exit(return_code)

    def verify(self):
        """Run Arduino program and verify a sketch."""
        # Check if arduino exists
        if self.__which(self.arduino_program) is None:
            erroln('Program not found: ' + self.arduino_program)
            sys.exit(True)
        # Build command
        cmd = self.arduino_program + \
            " --verify --board " + self.architecture + " " + \
            self.path + "/" + self.arduino_file
        if level() < 3:
            cmd += " >/dev/null 2>&1"
        infoln('Verifying...')
        return_code = os.system(cmd)
        if return_code != 0:
            erroln("Return code: " + str(return_code))
            if return_code > 127:
                return_code = 1
        infoln('')
        sys.exit(return_code)

    def upload(self):
        """Run Arduino program and upload a sketch."""
        # Check if arduino exists
        if self.__which(self.arduino_program) is None:
            erroln('Program not found: ' + self.arduino_program)
            sys.exit(True)
        # Build command
        infoln("Communication device: " + self.destination + ".")
        cmd = self.arduino_program + " --upload --board " + \
            self.architecture + " " + \
            self.path + "/" + self.arduino_file + \
            " --port " + self.destination
        if level() < 3:
            cmd += " >/dev/null 2>&1"
        infoln('Uploading...')
        return_code = os.system(cmd)
        if return_code == 0:
            f = open(self.logs + "/.buildno", 'r')
            buildno = f.read()
            f.close()
            if buildno == "":
                buildno = 1
            else:
                buildno = int(buildno) + 1
            f = open(self.logs + "/.buildno", 'w')
            f.write(str(buildno))
            infoln("Build number: " + str(buildno))
        else:
            erroln("Return code: " + str(return_code))
            if return_code > 127:
                return_code = 1
        infoln('')
        sys.exit(return_code)

    def __which(self, program):
        """ """
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        fpath, fname = os.path.split(program)
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
