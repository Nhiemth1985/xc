"""
---
name: control_mouse.py
description: Mouse Control
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


class ControlMouse:
    """
    description:
    """

    def __init__(self):
        self.__version__ = 0.1
        self.__work_dir = os.path.dirname(os.path.realpath(__file__))
        self.__work_dir = os.path.join(self.__work_dir, '../')
        self.__enable = False
        self.__factor = None
        self.__visible = False
        self.__mouse = None
        self.__mapping = {}
        self.reset()

    def factor(self, factor=None):
        """
        description:
        """
        if factor is not None:
            self.__factor = factor
        return self.__factor

    def visible(self, visible=None):
        """
        description:
        """
        if visible is not None:
            self.__visible = visible
            off = ("        ",  # sized 8x8
                   "        ",
                   "        ",
                   "        ",
                   "        ",
                   "        ",
                   "        ",
                   "        ")
            curs, mask = pygame.cursors.compile(off, ".", "X")
            cursor = ((8, 8), (5, 1), curs, mask)
            if self.__visible:
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
            else:
                pygame.mouse.set_cursor(*cursor)
        return self.__visible

    def reset(self):
        """
        description:
        """
        self.__enable = False
        self.__factor = 1
        self.__visible = False
        self.__mouse = None
        self.__mapping = {}

    def enable(self):
        """
        description:
        """
        self.state(True)

    def disable(self):
        """
        description:
        """
        self.state(False)

    def state(self, state=None):
        """
        description:
        """
        if state is not None:
            self.__enable = state
        pygame.event.set_grab(self.__enable)
        self.visible(not self.__enable)
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
        if event.type == MOUSEMOTION:  # pylint: disable=undefined-variable
            relative = pygame.mouse.get_rel()
            x = relative[0]  # pylint: disable=invalid-name,unused-variable
            y = relative[1]  # pylint: disable=invalid-name,unused-variable
            for i in self.__mapping:
                try:
                    i["control"]["mouse"]
                except BaseException:
                    continue
                if eval(i["control"]["mouse"]):
                    try:
                        peuda = eval(i["control"]["mouse"].split(" ")[0])
                        peuda = abs(peuda * self.__factor)
                        peuda = int(round(peuda))
                        i["factor"] = str(peuda)
                        i["button"].on()
                        if int(peuda) == 0:
                            continue
                    except BaseException:
                        pass
                else:
                    i["button"].off()

    def start(self):
        """
        description: Detect and start
        """
        # Check for device
        check_input = os.path.join(self.__work_dir, 'scripts/check_input.sh')
        cmd = [check_input, 'mouse']
        return_code = subprocess.call(cmd)
        if return_code == 0:
            self.__mouse = True

    def info(self):
        """
        description:
        """
        echo.info('Mouse: ', 1)
        if not self.__mouse:
            echo.infoln(str(self.__mouse))
            return
        echo.infoln('Found')
        echo.debugln('Enable: ' + str(self.__enable), 2)
        echo.debugln('Factor: ' + str(self.__factor), 2)
