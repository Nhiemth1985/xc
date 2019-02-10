"""
---
name: timer.py
description: Stepper motor package
copyright: 2014-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
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
    """

    def __init__(self, period, type="LOOP"):
        """
        """
        self.version = '0.08'
        self.millis = lambda: int(round(time.time() * 1000))
        self.period = period * 1.0
        self.type = type
        self.enable = True
        self.counter = self.millis()

    def set(self, period):
        """
        """
        self.period = period * 1.0
        self.reset()
        self.enable = True

    def get(self):
        """
        """
        return self.period

    def reset(self):
        """
        """
        self.enable = True
        self.counter = self.millis()

    def enable(self):
        """
        """
        self.enable = True

    def disable(self):
        self.enable = False

    def unit(self, unit):
        """
        Available units:
            s: seconds
            m: milliseconds
            u: microseconds
        """
        self.unit = unit

    def check(self):
        """
        """
        if self.type == "LOOP":
            if (self.millis() - self.counter >= self.period):
                self.counter = self.millis()
                return True
        elif self.type == "COUNTDOWN":
            if (self.millis() - self.counter >= self.period):
                self.enable = False
                return True
        elif self.type == "STOPWATCH":
            return self.millis() - self.counter
        else:
            return False

    def status(self):
        """
        """
        return (self.millis() - self.counter) / self.period
