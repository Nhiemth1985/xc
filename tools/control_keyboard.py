"""
---
name: control_keyboard.py
description: Keyboard Control
copyright: 2016-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  contributors:
  - name: None
change-log:
  2019-12-14
  - version: 0.1
    added: Scrach version.
"""

import os.path
import subprocess
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *  # pylint: disable=wildcard-import, unused-import, unused-wildcard-import
import tools.echo as echo


class ControlKeyboard:
    """
    description:
    """

    def __init__(self):
        self.__version__ = 0.1
        self.__work_dir = os.path.dirname(os.path.realpath(__file__))
        self.__work_dir = os.path.join(self.__work_dir, '../')
        self.__enable = False
        self.__delay = None
        self.__interval = None
        self.__keyboard = None
        self.__mapping = {}
        self.reset()

    def delay(self, delay=None):
        """
        description:
            When the keyboard repeat is enabled, keys that are held down will
            generate multiple pygame.KEYDOWN events. The delay parameter is the
            number of milliseconds before the first repeated pygame.KEYDOWN
            event will be sent.
        """
        if delay is not None:
            self.__delay = delay
        pygame.key.set_repeat(self.__delay, self.__interval)
        return self.__delay

    def interval(self, interval=None):
        """
        description:
            When the keyboard repeat is enabled, keys that are held down will
            generate multiple pygame.KEYDOWN events. The interval parameter is
            the number of milliseconds

            . If a delay value is provided and an interval value is not provided
            or is 0, then the interval will be set to the same value as delay.

            To disable key repeat call this function with no arguments or with
             delay set to 0.
        """
        if interval is not None:
            self.__interval = interval
        pygame.key.set_repeat(self.__delay, self.__interval)
        return self.__interval

    def reset(self):
        """
        description:
        """
        self.__enable = False
        self.__delay = 1  # milliseconds
        self.__interval = 1  # milliseconds
        self.__keyboard = None
        self.__mapping = {}

    def enable(self):
        """
        description:
        """
        self.__enable = True

    def disable(self):
        """
        description:
        """
        self.__enable = False

    def state(self, state=None):
        """
        description:
        """
        if state is not None:
            self.__enable = state
        return self.__enable

    def mapping(self, mapping=None):
        """
        description:
        """
        self.__mapping = mapping

    def handle(self, event):  # pylint: disable=too-many-branches
        """
        description:
        """
        if not self.__enable:
            return
        for i in self.__mapping:
            try:
                i["control"]["keyboard"]
            except BaseException:
                continue
            if i["type"] == "push-button":
                if event.type == KEYDOWN and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["button"].on()
                if event.type == KEYUP and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["button"].off()
            elif i["type"] == "switch":
                if event.type == KEYDOWN and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["button"].toggle()

    def start(self):
        """
        description: Detect and start
        """
        # Check for device
        check_input = os.path.join(self.__work_dir, 'scripts/check_input.sh')
        cmd = [check_input, 'keyboard']
        return_code = subprocess.call(cmd)
        if return_code == 0:
            self.__keyboard = True

    def info(self):
        """
        description:
        """
        echo.info('Keyboard: ', 1)
        if not self.__keyboard:
            echo.infoln(str(self.__keyboard))
            return
        echo.infoln('Found')
        echo.debugln('Enable: ' + str(self.__enable), 2)
        echo.debugln('Delay: ' + str(self.__delay) + 'ms', 2)
        echo.debugln('Interval: ' + str(self.__interval) + 'ms', 2)
