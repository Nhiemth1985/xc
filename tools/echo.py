"""
echo.py

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Description:
Verbosity:
    0 Quiet (no messages)
    1 Errors
    2 Warnings
    3 Info (all messages)
    4 Device code running

Change log:
2017-07-08
        * Version: 0.06
        * Added: debug function.
        * Added: debugln function.

2017-05-11
        * Version: 0.05b
        * Bug fix: Added flush to code output.

2017-04-01
        * Version: 0.04b
        * Improvement: Added version information.

2017-03-07
        * Version: 0.03b
        * Added colors to code output.

2017-02-26
        * Version: 0.02b
        * Added 'from __future__ import print_function' to be more proxy to
          addopt Python 3 style.

2017-02-20
        * Version: 0.01b
        * Added print() brackets to addopt Python 3 style.

2017-02-06
        * Version: 0.00b
        * Scrach version.
"""

from __future__ import print_function
import sys
from termcolor import cprint

INDENT_WIDTH = 4


class Echo(object):
    """
    description:
    """

    @classmethod
    def __init__(self):
        self.version = 0.06
        self.verbosity = a

    @classmethod
    def verbose(self, level):
        """
        description:
        """
        self.verbosity = level

    @classmethod
    def verbose_level(self):
        """
        description:
        """
        return int(self.verbosity)

    @classmethod
    def echo(self, string, level, indent=0):
        """
        description:
        """
        preffix = ''
        for i in range(indent * INDENT_WIDTH):
            preffix += ' '
        self.__print(preffix + string, level, '')

    @classmethod
    def echoln(self, string, level, indent=0):
        """
        description:
        """
        preffix = ''
        for i in range(indent * INDENT_WIDTH):
            preffix += ' '
        self.__print(preffix + string, level, '\n')

    @classmethod
    def __print(self, string, level, trailer):
        """
        description:
        """
        if int(level) <= int(self.verbosity):
            print(string, end=trailer)
            sys.stdout.flush()


def verbose(level):
    """
    description:
    """
    Echo.verbose(level)


def level():
    """
    description:
    """
    return Echo.verbose_level()


def echo(string, indent=0):
    """
    description:
    """
    Echo.echo(string, 0, indent)


def echoln(string, indent=0):
    """
    description:
    """
    Echo.echoln(string, 0, indent)


def erro(string, indent=0):
    """
    description:
    """
    Echo.echo('Error: ' + string, 1, indent)


def erroln(string, indent=0):
    """
    description:
    """
    Echo.echoln('Error: ' + string, 1, indent)


def warn(string, indent=0):
    """
    description:
    """
    Echo.echo('Warning: ' + string, 2, indent)


def warnln(string, indent=0):
    """
    description:
    """
    Echo.echoln('Warning: ' + string, 2, indent)


def info(string, indent=0):
    """
    description:
    """
    Echo.echo(string, 3, indent)


def infoln(string, indent=0):
    """
    description:
    """
    Echo.echoln(string, 3, indent)


def debug(string, indent=0):
    """
    description:
    """
    Echo.echo(string, 4, indent)


def debugln(string, indent=0):
    """
    description:
    """
    Echo.echoln(string, 4, indent)


def code(string, color=None, attrs=None):
    """
    description:
    """
    if level() < 4:
        return False
    if color is None:
        color = 'blue'
    if attrs is None:
        attrs = []
    cprint(string, color, attrs=attrs, end='')
    sys.stdout.flush()
    return False


def codeln(string, color=None, attrs=None):
    """
    description:
    """
    code(string + '\n', color, attrs)