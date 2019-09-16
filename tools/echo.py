"""
---
name: echo.py
description: Echo package
verbosity:
    0 Quiet (no messages)
    1 Errors
    2 Warnings
    3 Info (all messages)
    4 Device code running
copyright: 2017-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
  2019-09-07
  - version: 0.2
    fixed: pylint friendly.
  2017-07-08
  - version: 0.06
    added: debug function.
    added: debugln function.
  2017-05-11
  - version: 0.05b
    fixed: flush code output.
  2017-04-01
  - version: 0.04b
    added: Version information.
  2017-03-07
  - version: 0.03b
    added: colors code output.
  2017-02-26
  - version: 0.02b
    added: __future__ functions, more near to addopt Python 3 style.
  2017-02-20
  - version: 0.01b
    added: print() brackets to addopt Python 3 style.
  2017-02-06
  - version: 0.00b
    added: First version.
  """

import sys
from termcolor import cprint

INDENT_WIDTH = 4


class Echo():
    """
    description:
    """

    @classmethod
    def __init__(cls):
        cls.version = 0.2
        cls.verbosity = 0

    @classmethod
    def verbose(cls, verbosity=None):
        """
        description:
        """
        if verbosity is None:
            return int(cls.verbosity)
        cls.verbosity = verbosity
        return False

    @classmethod
    def echo(cls, string, verbosity, indent=0):
        """
        description:
        """
        preffix = ''
        for _ in range(indent * INDENT_WIDTH):
            preffix += ' '
        cls.__print(preffix + string, verbosity, '')

    @classmethod
    def echoln(cls, string, verbosity, indent=0):
        """
        description:
        """
        preffix = ''
        for _ in range(indent * INDENT_WIDTH):
            preffix += ' '
        cls.__print(preffix + string, verbosity, '\n')

    @classmethod
    def __print(cls, string, verbosity, trailer):
        """
        description:
        """
        if int(verbosity) <= int(cls.verbosity):
            print(string, end=trailer)
            sys.stdout.flush()


def verbose(verbosity):
    """
    description:
    """
    Echo.verbose(verbosity)


def level():
    """
    description:
    """
    return Echo.verbose()


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
