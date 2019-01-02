"""
timer.py

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log:
2017-06-29
        * Version: 0.03b
        * Bug fix: Some minor fixes.

2017-06-28
        * Version: 0.02b
        * New feature: Added get method.
        * New feature: Added status method.
        * Improvement: Added status to check method.
        * Improvement: Changed requied library "datetime" to "time".

2017-04-01
        * Version: 0.01b
        * Improvement: Added version information.

2016-02-13
        * Version: 0.00b
        * Scrach version.
"""

import time


class Timer:
    """
    """

    def __init__(self, period, type="LOOP"):
        """
        """
        self.version = '0.03b'
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
