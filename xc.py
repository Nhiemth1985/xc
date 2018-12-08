#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
xc.py

Description: Main program file

Copyright (c) 2014-2018 Márcio Pessoa

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log: Check CHANGELOG.md file.

"""

try:
    # Ubuntu default modules
    import sys
    import argparse
    import os.path
    import time
    # Myself modules
    from xC.device import DeviceProperties
    from xC.echo import verbose, level, \
        echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln
    from xC.file import File
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
        self.program_version = "0.61b"
        self.program_date = "2018-11-22"
        self.program_description = "xC - aXes Controller"
        self.program_copyright = "Copyright (c) 2014-2018 Marcio Pessoa"
        self.program_license = "undefined. There is NO WARRANTY."
        self.program_website = "http://pessoa.eti.br/"
        self.program_contact = "Marcio Pessoa <marcio.pessoa@gmail.com>"
        self.id = None
        self.interface = None
        self.config_file = os.path.join(os.getenv('HOME', ''), '.xC.json')
        header = ('xc <command> [<args>]\n\n' +
                  'commands:\n' +
                  '  gui            graphical user interface\n' +
                  '  terminal       connect to device terminal\n' +
                  '  verify         check firmware code sintax\n' +
                  '  upload         upload firmware to device\n' +
                  '  run            run a program\n' +
                  '  list           list devices\n\n')
        footer = (self.program_copyright + '\n' +
                  'License: ' + self.program_license + '\n' +
                  'Website: ' + self.program_website + '\n' +
                  'Contact: ' + self.program_contact + '\n')
        examples = ('examples:\n' +
                    '  xc list\n' +
                    '  xc verify --id x6 --verbosity=3\n' +
                    '  xc upload\n' +
                    '  xc gui --id x2\n' +
                    '  xc run -i x6 -p file.gcode\n')
        self.version = (self.program_name + " " + self.program_version + " (" +
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
            echoln('Unrecognized command')
            parser.print_help()
            sys.exit(True)
        getattr(self, args.command)()

    def run(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' run',
            description='connect to device terminal')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '-p', '--program', metavar='file',
            required=True,
            help='load G-code file')
        parser.add_argument(
            '-v', '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        infoln(self.version)
        self.__load_configuration()
        infoln('Loading program...')
        program = File()
        program.load(args.program, 'gcode')
        self.__connection(args.id, 'serial')
        self.session.set_program(program.get())
        self.session.run()
        sys.exit(False)

    def gui(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' gui',
            description='graphical user interface')
        parser.add_argument(
            '-i', '--id',
            help='device ID')
        parser.add_argument(
            '-v', '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        infoln(self.version)
        from xC.gui import Gui
        self.__load_configuration()
        gui = Gui(self.config.get())
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
            '-v', '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        infoln(self.version)
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
            '-v', '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        infoln(self.version)
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
            '-v', '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info, 4 Code')
        args = parser.parse_args(sys.argv[2:])
        verbose(args.verbosity)
        infoln(self.version)
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
            '-a', '--all', action="store_true",
            help='show even disabled devices')
        parser.add_argument(
            '-v', '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3, 4],
            help='verbose mode, options: ' +
                 '0 Quiet (return number of devices), 1 IDs (default),' +
                 ' 2 Names, 3 Status, 4 Description')
        args = parser.parse_args(sys.argv[2:])
        self.__load_configuration()
        device = DeviceProperties(self.config.get())
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
        for id in device.list():
            device.set(id)
            session = Session(device.get_comm())
            if not args.all and not device.is_enable():
                    continue
            if args.verbosity >= 4 or args.connected:
                interface = 'Offline'
                args.interface = 'serial'
                if args.interface == 'serial' or args.interface == 'all':
                    if session.is_connected_serial():
                        interface = "Serial"
                if args.interface == 'network' or args.interface == 'all':
                    if session.is_connected_network():
                        interface = "Network"
            if args.connected and interface == 'Offline':
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
        sys.exit(False)

    def __load_configuration(self):
        infoln('Loading configuration...')
        self.config = File()
        self.config.load(self.config_file, 'json')

    def __connection(self, id=None, interface=None):
        self.__device_select(id)
        if interface:
            self.interface = interface
            self.session = Session(self.device.get_comm())
            self.session.info()
            if self.interface == 'serial':
                if self.session.is_connected_serial():
                    self.session.start()
                else:
                    warnln('Device is not connected.', 1)
                    sys.exit(True)
            elif self.interface == 'network':
                if self.device.comm_network_address is None:
                    erroln("Interface not configured for this device.")
                    sys.exit(True)
                if not self.device.is_network_connected():
                    erroln('Device is not reacheable: ' +
                           str(self.device.comm_network_address))
                    sys.exit(True)

    def __device_select(self, id=None):
        infoln('Device...')
        self.device = DeviceProperties(self.config.get())
        if id:
            self.id = id
            self.device.set(self.id)
            self.device.info()
            return
        n = self.device.detect()
        if len(n) < 1:
            erroln('Device not connected.', 1)
            sys.exit(True)
        if len(n) > 1:
            erroln('Too many connected devices: ' + str(n), 1)
            sys.exit(True)
        if len(n) == 1:
            self.id = self.device.get_id()
            self.device.info()
            return

    def __dev_tools(self, id=None, date=False, interface=None):
        if date:
            infoln('Started at: ' + time.strftime('%Y-%m-%d %H:%M:%S'))
        if interface:
            self.interface = interface
        self.__load_configuration()
        self.__device_select(id)
        self.project = DevTools(self.device.get())
        self.project.info()
        self.session = Session(self.device.get_comm())
        self.session.info()
        if self.interface:
            # infoln("Connecting...", 1)
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
