"""
---
name: timer.py
description: Timer package
copyright: 2014-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
  2019-08-25
  - version: 0.09
    fixed: Some adequations to pylint3.
  2017-06-29
  - version: 0.08
    fixed: Some minor fixes.
  2017-06-28
  - version: 0.07
    added: get method.
    added: status method.
    added: status to check method.
    changed: Requied library "datetime" to "time".
  2017-04-01
  - version: 0.06
    added: version information.
  2016-02-13
  - version: 0.05
    added: Ported from C++ to Python.
  2015-10-04
  - version: 0.04
    fixed: COUNTDOWN timer. Now counter stop decreasing after reaches 0.
  2015-09-27
  - version: 0.03
    added: residual method.
  2014-11-16
  - version: 0.02
    changed: Timer (int period) to (unsigned long period).
    changed: set (int period) to (unsigned long period).
  2014-07-06
  - version: 0.01
    added: Staring a new library.
"""

import time


class Timer:
    """
    description:
    """

    def __init__(self, period, style="LOOP"):
        self.version = 0.09
        self.millis = lambda: int(round(time.time() * 1000))
        self.period = period * 1.0
        self.__style = style
        self.__enable = True
        self.__unit = None
        self.counter = self.millis()

    def set(self, period):
        """
        description:
        """
        self.period = period * 1.0
        self.reset()

    def get(self):
        """
        description:
        """
        return self.period

    def reset(self):
        """
        description:
        """
        self.counter = self.millis()

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

    def unit(self, unit):
        """
        description:
            - Available units:
                s: seconds
                m: milliseconds
                u: microseconds
        """
        self.__unit = unit

    def check(self):
        """
        description:
        """
        if not self.__enable:
            return False
        if self.__style == "LOOP":
            if self.millis() - self.counter >= self.period:
                self.counter = self.millis()
                return True
        if self.__style == "COUNTDOWN":
            if self.millis() - self.counter >= self.period:
                self.__enable = False
                return True
        if self.__style == "STOPWATCH":
            return self.millis() - self.counter
        return False

    def status(self):
        """
        description:
        """
        return self.millis() - self.counter
