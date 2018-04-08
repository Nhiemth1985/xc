"""
fan.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2017-06-29
        * Version: 0.01b
        * Bug fix: Some minor fixes.

2017-06-28
        * Version: 0.00b
        * First version.

"""

import math
from timer import Timer


class SigGen():
    """
    """

    def __init__(self):
        """
        Description
            Blink LED without delay function.

            RealTime (int pin, int millis_period, boolean state)

        Parameters
            pin: Arduino LED pin
            millis_period: Time period to define blink delay (milliseconds)
            state: Initial LED state

        Returns
            void
        """
        self.version = '0.01b'
        self.timer = Timer(1000)

    def period(self, period):
        """
        Description
            Sine wave.

            object.sine()

        Parameters
            void

        Returns
            float: sine signal
        """
        self.timer.set(period)

    def sine(self):
        """
        Description
            Sine wave.

            object.sine()

        Parameters
            void

        Returns
            float: sine signal
        """
        y = ((-math.cos((self.step() * math.pi) * 2.0)) + 1) / 2
        return y

    def square(self):
        """
        Description
            Square wave.

            object.square()

            Waveform with 1000 milliseconds duration:

            1 ┐    ┌────┐
              │    │    │
              └────┘    └
              0   500   1000

        Parameters
            void

        Returns
            float: square signal
        """
        if self.step() < 0.5:
            y = 0
        else:
            y = 1
        return y

    def step(self):
        """
        Description
            A time baseline to provide x axis to signal generation.

            step()

        Parameters
            void

        Returns
            float: time baseline from 0 to 1.
        """
        self.timer.check()
        return self.timer.status()
