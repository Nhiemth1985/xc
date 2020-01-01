"""
---
name: control_touch.py
description: Touch Control
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
import tools.echo.echo as echo
from tools.cursor_mouse import cursor_mouse


class ControlTouch:
    """
    description:
    """

    __version__ = 0.1

    def __init__(self):
        self.__work_dir = os.path.dirname(os.path.realpath(__file__))
        self.__work_dir = os.path.join(self.__work_dir, '../')
        self.__enable = False
        self.__visible = False
        self.__touch = None
        self.__mapping = {}
        self.reset()

    def visible(self, visible=None):
        """
        description:
        """
        if visible is not None:
            self.__visible = visible
            cursor_mouse(self.__visible)
        return self.__visible

    def reset(self):
        """
        description:
        """
        self.__enable = False
        self.__visible = False
        self.__touch = None
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
            if i["type"] == 'push-button':
                if event.type == MOUSEBUTTONDOWN:  # pylint: disable=undefined-variable
                    i["button"].check(pygame.mouse.get_pos())
                if event.type == MOUSEBUTTONUP:  # pylint: disable=undefined-variable
                    i["button"].off()
            elif i["type"] == 'switch':
                if event.type == MOUSEBUTTONUP:  # pylint: disable=undefined-variable
                    i["button"].check(pygame.mouse.get_pos())

    def start(self):
        """
        description: Detect and start
        """
        # Check for device
        check_input = os.path.join(self.__work_dir, 'scripts/check_input.sh')
        cmd = [check_input, 'mouse']
        return_code = subprocess.call(cmd)
        if return_code == 0:
            self.__touch = True

    def info(self):
        """
        description:
        """
        echo.info('Touch: ', 1)
        if not self.__touch:
            echo.infoln(str(self.__touch))
            return
        echo.infoln('Found')
        echo.debugln('Enable: ' + str(self.__enable), 2)
        echo.debugln('Cursor: ' + 'Visible' if self.__enable else 'Hidden', 2)
