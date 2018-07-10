#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
xc.py

Copyright (c) 2014-2018 Márcio Pessoa <marcio.pessoa@sciemon.com>

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log: Check CHANGELOG.md file.

"""

try:
    # Ubuntu default modules
    import sys
    import argparse
    import os.path
    import time
    # Ubuntu manually installed modules
    import serial
    # Myself modules
    from xC.device import DeviceProperties
    from xC.echo import verbose, level, \
        echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln
    from xC.file import FileManagement
    from xC.host import HostProperties
    from xC.session import Session
    from xC.tools import DevTools
except ImportError as err:
    print("Could not load module. " + str(err))
    sys.exit(True)


class UserArgumentParser():
    """
    https://docs.python.org/2/library/argparse.html
    http://chase-seibert.github.io/blog/
    """

    # Set default verbosity level
    verbose(1)  # Error level

    def __init__(self):
        self.program_name = "xc"
        self.program_version = "0.54b"
        self.program_date = "2018-06-20"
        self.program_description = "xC - aXes Controller"
        self.program_copyright = "Copyright (c) 2014-2018 Marcio Pessoa"
        self.program_license = "undefined. There is NO WARRANTY."
        self.program_website = "http://pessoa.eti.br/"
        self.program_contact = "Marcio Pessoa <marcio.pessoa@sciemon.com>"
        self.id = None
        self.interface = None
        self.config_file = os.path.join(os.getenv('HOME', ''), '.xC.json')
        header = ('xc <command> [<args>]\n\n' +
                  'commands:\n' +
                  '  gui            graphical user interface\n' +
                  '  cli            command line interface\n' +
                  '  terminal       connect to device terminal\n' +
                  '  verify         check firmware code sintax\n' +
                  '  upload         upload firmware to device\n' +
                  '  list           list devices\n\n')
        footer = (self.program_copyright + '\n' +
                  'License: ' + self.program_license + '\n' +
                  'Website: ' + self.program_website + '\n' +
                  'Contact: ' + self.program_contact + '\n')
        examples = ('examples:\n' +
                    '  xc list\n' +
                    '  xc verify --id x6 --verbosity=3\n' +
                    '  xc upload -i envmon --interface=network\n' +
                    '  xc gui --id x2\n' +
                    '  xc cli -i x6 -p file.gcode -r\n')
        version = (self.program_name + " " + self.program_version + " (" +
                   self.program_date + ")" + '' + '\n')
        epilog = (examples + '\n' + footer)
        parser = argparse.ArgumentParser(
            prog=self.program_name,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog,
            add_help=True,
            usage=header)
        parser.add_argument('command', help='command to run')
        parser.add_argument('-v', '--version', action='version',
                            version=version,
                            help='show version information and exit')
        if len(sys.argv) < 2:
            self.gui()
            sys.exit(False)
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            echoln('Unrecognized command')
            parser.print_help()
            sys.exit(True)
        getattr(self, args.command)()

    def cli(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' cli',
            description='connect to device terminal')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '--interface',
            default='serial',
            choices=['serial', 'network'],
            help='communication interface (default: serial)')
        # parser.add_argument(
            # '-l', '--log', metavar='file',
            # help='log file')
        # parser.add_argument(
            # '-o', '--out', metavar='file',
            # help='output file')
        parser.add_argument(
            '-p', '--program', metavar='file',
            help='load G-code file')
        # parser.add_argument(
            # '-r', '--run', action="store_true",
            # help='run program')
        parser.add_argument(
            '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        # Start CLI
        from xC.cli import Cli
        if self.__connection(args.id, args.interface):
            sys.exit(True)
        # Start G-code parser
        gcode = CommandParser(self.ser)
        if gcode.load(args.program):
            erroln("Fail reading file: " + args.program)
            sys.exit(True)
        gcode.run()
        sys.exit(False)

    def gui(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' gui',
            description='graphical user interface')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '--interface',
            default='serial',
            choices=['serial', 'network'],
            help='communication interface (default: serial)')
        # parser.add_argument(
            # '-l', '--log', metavar='file',
            # help='log file')
        # parser.add_argument(
            # '-o', '--out', metavar='file',
            # help='output file')
        # parser.add_argument(
            # '-p', '--program', metavar='file',
            # help='load G-code file')
        # parser.add_argument(
            # '-r', '--run', action="store_true",
            # help='run program')
        parser.add_argument(
            '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        config = FileManagement(self.config_file)
        # Start GUI
        from xC.gui import Gui
        gui = Gui(config.get())
        if args.id:
            gui.device_set(args.id)
        gui.start()
        gui.run()
        sys.exit(False)

    def terminal(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' terminal',
            description='command line interface')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '--interface',
            default='serial',
            choices=['serial', 'network'],
            help='communication interface (default: serial)')
        parser.add_argument(
            '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        self.__dev_tools(args.id, args.interface)
        self.project.terminal()

    def verify(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' verify',
            description='check firmware code')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '-d', '--date', action="store_true",
            help='display date')
        parser.add_argument(
            '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        self.__dev_tools(args.id, args.date)
        self.project.verify()

    def upload(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' upload',
            description='upload firmware to device')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '-d', '--date', action="store_true",
            help='display date')
        parser.add_argument(
            '--interface',
            default='serial',
            choices=['serial', 'network'],
            help='communication interface (default: serial)')
        parser.add_argument(
            '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        self.__dev_tools(args.id, args.date, args.interface)
        self.project.upload()

    def list(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' list',
            description='list devices')
        parser.add_argument(
            '-c', '--connected', action="store_true",
            help='show only connected devices')
        parser.add_argument(
            '--interface',
            default='all',
            choices=['all', 'serial', 'network'],
            help='communication interface (default: all)')
        parser.add_argument(
            '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet (return number of devices), 1 IDs (default),' +
                 ' 2 Names, 3 Status, 4 Description')
        args = parser.parse_args(sys.argv[2:])
        config = FileManagement(self.config_file)
        device = DeviceProperties(config.get())
        if args.verbosity >= 2:
            echo(' Id\tName\tMark')
        if args.verbosity >= 3:
            echo('\tDescription')
        if args.verbosity >= 4:
            echo('\t\tLink')
        if args.verbosity > 1:
            echoln('')
        if args.verbosity >= 2:
            echo('------------------------')
        if args.verbosity >= 3:
            echo('------------------------')
        if args.verbosity >= 4:
            echo('--------')
        if args.verbosity > 1:
            echoln('')
        c = 0
        for id in device.list():
            device.set(id)
            session = Session(device.get_comm())
            if not device.is_enable():
                continue
            if args.verbosity >= 4 or args.connected:
                interface = 'Offline'
                if args.interface == 'serial' or args.interface == 'all':
                    if session.is_connected_serial():
                        interface = "Serial"
                if args.interface == 'network' or args.interface == 'all':
                    if session.is_connected_network():
                        interface = "Network"
            if args.connected and interface == '-':
                continue
            if args.verbosity >= 1:
                echo(id)
            if args.verbosity >= 2:
                echo("\t" +
                     device.system_plat + "\t" +
                     device.system_mark)
            if args.verbosity >= 3:
                echo('\t' + device.system_desc)
                if len(device.system_desc) < 16:
                    for i in range(16-len(device.system_desc)):
                        echo(" ")
            if args.verbosity >= 4:
                echo('\t' + interface)
            if args.verbosity > 0:
                echoln('')
            c += 1
        sys.exit(c)

    def __connection(self, id=None, interface=None):
        # Load device configuration file
        config = FileManagement(self.config_file)
        self.device = DeviceProperties(config.get())
        # Select device
        if id:
            self.id = id
            self.device.select(self.id)
        else:
            if self.device.select_auto():
                self.device.info()
            else:
                return False
        # Connect to device
        if interface:
            self.interface = interface
            infoln("Connecting...")
            if self.interface == 'serial':
                if self.session.is_connected_serial():
                    self.ser = serial.Serial(
                        self.device.comm_serial_path,
                        self.device.comm_serial_speed,
                        timeout=1)
                else:
                    warnln('Device is not connected.', 1)
                    return True
            elif self.interface == 'network':
                if self.device.comm_network_address is None:
                    erroln("Interface not configured for this device.")
                    return True
                if not self.device.is_network_connected():
                    erroln('Device is not reacheable: ' +
                           str(self.device.comm_network_address))
                    return True

    def __dev_tools(self, id=None, date=False, interface=None):
        if id:
            self.id = id
        if interface:
            self.interface = interface
        if date:
            infoln('Started at: ' + time.strftime('%Y-%m-%d %H:%M:%S'))
        # Load device configuration file
        config = FileManagement(self.config_file)
        infoln('Device...')
        self.device = DeviceProperties(config.get())
        if self.id is None:
            self.id = self.device.detect()
        else:
            self.device.set(self.id)
        if not self.id:
            erroln('Device not selected.', 1)
            sys.exit(True)
        self.device.info()
        self.project = DevTools(self.device.get_id())
        self.project.info()
        self.session = Session(self.device.get_comm())
        self.session.info()
        if self.interface:
            infoln("Connecting...", 1)
            if self.interface == 'serial':
                if not self.session.is_connected_serial():
                    erroln('Serial device is not connected.', 2)
                    sys.exit(True)
            elif self.interface == 'network':
                if self.device.comm_network_address is None:
                    erroln("Network interface not configured for this device.")
                    sys.exit(True)
                if not self.session.is_connected_network():
                    erroln('Network device is not reacheable.')
                    infoln('Check device connectivity: ' +
                           str(self.device.comm_network_address))
                    sys.exit(True)


def main():
    UserArgumentParser()


if __name__ == '__main__':
    main()
