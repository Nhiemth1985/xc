"""
---
name: control_joystick.py
description: Joystick Control
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
    fixed: info method was breking when joystick not found
  2019-10-12
  - version: 0.01
    added: Scrach version.
"""

import re
from pygame.locals import *  # pylint: disable=wildcard-import, unused-import, unused-wildcard-import
import tools.echo as echo
from tools.timer.timer import Timer
import tools.joystick.joystick as joystick


class ControlJoystick:
    """
    description:
    """

    def __init__(self):
        self.__version__ = 0.1
        self.__enable = False
        self.__factor = 1
        # self.__quiet = False
        self.__scan_time = 1000  # milliseconds
        self.__scan_timer = Timer(self.__scan_time)
        self.__joystick = None
        self.__mapping = {}
        self.reset()

    def reset(self):
        """
        description:
        """
        self.__enable = False
        self.__factor = 1
        # self.__quiet = False
        self.__scan_time = 1000  # milliseconds
        self.__scan_timer = None
        self.__joystick = None
        self.__mapping = {}

    def period(self, time=False):
        """
        description: Set scan period

        parameters:
          time: scan time period (integer >= 1000)

        returns:
          int: scan time period
        """
        if time >= 1000:
            self.__scan_time = time
            self.__scan_timer = Timer(self.__scan_time)
        return self.__scan_time

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

    def factor(self, factor):
        """
        description:
        """
        self.__factor = factor

    def mapping(self, mapping=None):
        """
        description:
        """
        if not mapping:
            print(json_pretty(self.__mapping))
        self.__mapping = mapping

    def handle(self, event):  # pylint: disable=too-many-branches
        """
        description:
        """
        if not self.__enable:
            return
        # Buttons
        for i in self.__mapping:
            try:
                if i["control"]["joystick"].split("[")[0] != "button":
                    continue
            except BaseException:
                continue
            i["source"] = ''
            button = int(re.findall('\\b\\d+\\b', i["control"]["joystick"])[0])
            if self.__joystick.button()[button] and \
               event.type == JOYBUTTONDOWN:  # pylint: disable=undefined-variable
                i["source"] = 'joystick'
                if i["type"] == "switch":
                    i["button"].toggle()
                elif i["type"] == "push-button":
                    i["button"].on()
            else:
                if i["type"] == "push-button" and \
                   event.type == JOYBUTTONUP:  # pylint: disable=undefined-variable
                    i["button"].off()
        # Digital motion (hat)
        # if (event.type == JOYHATMOTION or self.joystick_hat_active):
            # for i in self.device.get_objects():
                # try:
                    # i["control"]["joystick"]
                # except BaseException:
                    # continue
                # if i["control"]["joystick"].split("[")[0] == "hat":
                    # hat = []
                    # for j in range(self.joystick.get_numhats()):
                        # hat.append(self.joystick.get_hat(j))
                        # infoln("hat[" + str(j) + "] = " + str(hat[j]))
                    # if 1 in hat[0] or -1 in hat[0]:
                        # self.joystick_hat_active = True
                    # else:
                        # self.joystick_hat_active = False
                    # if eval(i["control"]["joystick"]):
                        # i["button"].on()
                    # else:
                        # i["button"].off()
        # Analog motion
        if event.type == JOYAXISMOTION:  # pylint: disable=undefined-variable
            for i in self.__mapping:
                try:
                    i["control"]["joystick"]
                except BaseException:
                    continue
                if i["control"]["joystick"].split("[")[0] == "axis":
                    axis = re.findall(
                        '\\b\\d+\\b',
                        i["control"]["joystick"])
                    axis = int(axis[0])
                    signal = 0
                    if i["control"]["joystick"][-1:] == "+":
                        signal = 1
                    elif i["control"]["joystick"][-1:] == "-":
                        signal = -1
                    value = self.__joystick.axis()[axis]
                    if value * signal * 1000 > 1:
                        i["button"].on()
                        factor = abs(value * self.__factor)
                        i["factor"] = str(factor)
                    else:
                        i["button"].off()
                        i["factor"] = '1'

    def start(self):
        """
        description: Detect and start
        """
        self.__joystick = joystick.Joystick()
        detected = joystick.detect()
        if detected:
            self.__joystick.identification(detected[0])
        else:
            if self.__joystick:
                self.reset()

    def info(self):
        """
        description:
        """
        echo.info('Joystick: ', 1)
        if not self.__joystick:
            echo.infoln(str(self.__joystick))
            return
        echo.infoln(str(self.__joystick.configuration()['name']))
        echo.debugln('Enable: ' + str(self.__enable), 2)
        echo.debugln('Axes: ' + str(self.__joystick.configuration()['axes']), 2)
        echo.debugln('Buttons: ' + str(self.__joystick.configuration()['buttons']), 2)
        echo.debugln('Balls: ' + str(self.__joystick.configuration()['balls']), 2)
        echo.debugln('Hats: ' + str(self.__joystick.configuration()['hats']), 2)
        echo.debugln('Factor: ' + str(self.__factor), 2)


def json_pretty(data):
    """
    description:
    """
    import json
    return json.dumps(data, indent=2, separators=(", ", ": "))
