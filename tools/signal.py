"""
---
name: signal.py
description: Signal Generator package
copyright: 2017-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
  2017-06-29
  - version: 0.01b
    fixed: Some minor fixes.
  2017-06-28
  - version: 0.00b
    added: First version.
"""

import math
from timer.timer import Timer


class SigGen():
    """
    description:
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
        self.version = 0.01
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
        spread = ((-math.cos((self.step() * math.pi) * 2.0)) + 1) / 2
        return spread

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
            spread = 0
        else:
            spread = 1
        return spread

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
