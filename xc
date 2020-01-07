#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
---
name: xc.py
description: Main program file
copyright: 2014-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log: Check CHANGELOG.md file.
"""

# Check Python version
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
    print("This progarm requires Python 3.6 or higher!")
    print("You are using Python {}.{}." .
          format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

# Check and import modules
try:
    # Ubuntu default modules
    import argparse
    import os.path
    # Myself modules
    import tools.echo.echo as echo
    from tools.device.device import DeviceProperties
    from tools.file.file import File
    from tools.session.session import Session
except ImportError as err:
    print("Could not load module. " + str(err))
    sys.exit(True)


class XC():  # pylint: disable=too-many-instance-attributes
    """
    description:
    reference:
    - Links
      https://docs.python.org/2/library/argparse.html
      http://chase-seibert.github.io/blog/
    """

    __version__ = 0.84

    def __init__(self):
        self.program_name = "xc"
        self.program_date = "2019-12-22"
        self.program_description = "xc - aXes Controller"
        self.program_copyright = "Copyright (c) 2014-2019 Marcio Pessoa"
        self.program_license = "undefined. There is NO WARRANTY."
        self.program_website = "https://github.com/marcio-pessoa/xc"
        self.program_contact = "Marcio Pessoa <marcio.pessoa@gmail.com>"
        self.__id = None
        self.interface = None
        self.project = None
        self.device = None
        self.config = None
        self.host = None
        self.session = None
        self.config_file = os.path.join(os.getenv('HOME', ''), '.device.json')
        header = (self.program_name + ' <command> [<args>]\n\n' +
                  'commands:\n' +
                  '  gui            graphical user interface\n' +
                  '  terminal       connect to device terminal\n' +
                  '  run            run a program\n\n')
        footer = (self.program_copyright + '\n' +
                  'License: ' + self.program_license + '\n' +
                  'Website: ' + self.program_website + '\n' +
                  'Contact: ' + self.program_contact + '\n')
        examples = ('examples:\n' +
                    '  ' + self.program_name + ' terminal \n' +
                    '  ' + self.program_name + ' gui --id x2\n' +
                    '  ' + self.program_name + ' run -i x6 -p file.gcode\n')
        self.version = (self.program_description + " " +
                        str(self.__version__) + " (" +
                        self.program_date + ")")
        epilog = (examples + '\n' + footer)
        parser = argparse.ArgumentParser(
            prog=self.program_name,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog,
            add_help=True,
            usage=header)
        parser.add_argument('command', help='command to run')
        parser.add_argument('-V', '--version', action='version',
                            version=self.version,
                            help='show version information and exit')
        if len(sys.argv) < 2:
            self.gui()
            sys.exit(False)
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            echo.echoln('Unrecognized command')
            parser.print_help()
            sys.exit(True)
        getattr(self, args.command)()

    def gui(self):
        """
        description:
        """
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' gui',
            description='Graphical user interface')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '-v', '--verbosity', type=int,
            default=4,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
            '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Debug')
        args = parser.parse_args(sys.argv[2:])
        echo.level(args.verbosity)
        echo.infoln(self.version)
        from tools.gui import Gui
        self.__load_configuration()
        gui = Gui(self.config.get())
        gui.device_set(args.id)
        gui.start()
        gui.run()
        sys.exit(False)

    def run(self):
        """
        description:
        """
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' run',
            description='Run a program on device')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '-p', '--program', metavar='file',
            required=True,
            help='load G-code file')
        parser.add_argument(
            '-v', '--verbosity', type=int,
            default=4,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
            '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Debug')
        args = parser.parse_args(sys.argv[2:])
        echo.level(args.verbosity)
        echo.infoln(self.version)
        self.__load_configuration()
        echo.infoln('Loading program...')
        program = File()
        program.load(args.program, 'gcode')
        self.__connection(args.id, 'serial')
        self.session.set_program(program.get())
        self.session.run()
        sys.exit(False)

    def terminal(self):
        """
        description:
        """
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' terminal',
            description='Connect to device console')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '-v', '--verbosity', type=int,
            default=3,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
            '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Debug')
        args = parser.parse_args(sys.argv[2:])
        self.__id = args.id
        echo.level(args.verbosity)
        echo.infoln(self.version)
        self.__terminal()

    def __load_configuration(self):
        echo.infoln('Loading configuration...')
        self.config = File()
        self.config.load(self.config_file, 'json')

    def __connection(self, device_id=None, interface=None):
        self.__device_select(device_id)
        if interface:
            self.interface = interface
            self.session = Session(self.device.get_comm())
            self.session.info()
            if self.interface == 'serial':
                if self.session.is_connected_serial():
                    self.session.start()
                else:
                    echo.erroln('Device is not connected.', 1)
                    sys.exit(True)

    def __device_select(self, device_id=None):
        echo.infoln('Device...')
        self.device = DeviceProperties(self.config.get())
        if device_id:
            self.__id = device_id
            self.device.set(self.__id)
            self.device.info()
            return
        devices_list = self.device.detect()
        devices = len(self.device.detect())
        if devices < 1:
            echo.erroln('Device not connected.', 1)
            sys.exit(True)
        if devices > 1:
            echo.erroln('Too many connected devices: ' + str(devices_list), 1)
            sys.exit(True)
        if devices == 1:
            self.__id = self.device.get_id()
            self.device.info()
            return

    def __terminal(self):
        """
        description:
        """
        from serial.tools.miniterm import Miniterm
        self.__load_configuration()
        echo.infoln('Device...')
        device = DeviceProperties(self.config.get())
        device.set(self.__id)
        terminal_echo = False
        terminal_end_of_line = 'LF'
        if 'serial' not in device.get_comm():
            echo.erroln("Missed configuration field: 'serial'")
            sys.exit(True)
        if 'terminal_echo' in device.get_comm()['serial']:
            terminal_echo = device.get_comm()['serial']['terminal_echo']
        if 'terminal_end_of_line' in device.get_comm()['serial']:
            terminal_end_of_line = device.get_comm()['serial']['terminal_end_of_line']
        echo.infoln(
            "Communication device: " +
            os.popen("readlink -f " +
                     device.get_comm()['serial']['path']).read().rstrip(), 1)
        # Start serial session
        session = Session(device.get_comm())
        instance = session.start()
        if instance is True:
            sys.exit(True)
        # Start minicom session
        miniterm = Miniterm(instance,
                            echo=terminal_echo,
                            eol=terminal_end_of_line.lower(),
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


def main():
    """
    description:
    """
    XC()


if __name__ == '__main__':
    main()
