"""
fan.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2017-07-20
        * Version: 0.02b
        * New feature: Method setLimits() to pre define temperature limits.
        * New feature: Method autoSpeed()
        * Improvement: Added function map().
        * Improvement: Added function constrain().

2017-06-27
        * Version: 0.01b
        * Bug fix: Some minor fixes.

2017-06-25
        * Version: 0.00b
        * First version.
"""

import RPi.GPIO as GPIO
from xC.timer import Timer


class Fan():
    """
    Fan speed control.
    """

    """
    Description
        Fan speed control.

        Fan (write_pin, read_pin)

    Parameters
        write_pin: Arduino LED connected to PWM motor controller
        read_pin: Arduino pin connected to motor sensor pin

    Returns
        void
    """
    def __init__(self, write_pin, read_pin=None, max_speed=3000):
        self.version = '0.02b'
        self.read_pin = read_pin  # Pin number
        self.write_pin = write_pin  # Pin number
        self.max_speed = max_speed  # RPM
        self.speed = 100  # Initial speed
        self.is_sensor_present = False
        self.rpm = 0
        self.counter_rpm = 0
        self.sample_rate = 30  # Sample rate (per minute)
        self.delta_t = 60.0 / self.sample_rate * 1000  # Interval (per seconds)
        self.timer = Timer(self.delta_t)
        self.bounce = 1000 / (self.max_speed * 2 / 60)  # Bounce time
        self.limit_min = 0
        self.limit_max = 100
        # setmode
        # Available modes:
        #     GPIO.BOARD: Board numbering scheme. The pin numbers follow the pin
        #                 numbers on header P1.
        #     GPIO.BCM: Broadcom chip-specific pin numbers. These pin numbers
        #               follow the lower-level numbering system defined by the
        #               Raspberry Pi’s Broadcom-chip brain.
        GPIO.setmode(GPIO.BOARD)
        # Set fan control pin
        GPIO.setup(self.write_pin, GPIO.OUT)
        # Set PWM control
        self.fan_controller = GPIO.PWM(self.write_pin, self.speed)
        self.fan_controller.start(self.speed)
        if self.read_pin is not None:
            self.is_sensor_present = True
            # Set fan sensor pin
            # pull_up_down: Internal Pull-ups and Pull-down resistors.
            # Available options:
            #     GPIO.PUD_UP: Pull up
            #     GPIO.PUD_DOWN: Pull down
            GPIO.setup(self.read_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # Add interrupt detection
            GPIO.add_event_detect(self.read_pin, GPIO.RISING,
                                  callback=self.counter, bouncetime=self.bounce)

    """
    Description
        Just a counter.

    Parameters
        none

    Returns
        void
    """
    def counter(self, channel):
        if not self.is_sensor_present:
            self.counter_rpm = 0
            return True
        # Count
        self.counter_rpm += 1
        if self.timer.check():
            self.rpm = int(self.counter_rpm / self.delta_t * 1000 * 60 / 2.0)
            self.counter_rpm = 0
            return False

    """
    Description
     *   Change fan speed value.

     *   fan.speedWrite(int percent_speed)

     * Parameters
     *   percent_speed: Fan percent speed

     * Returns
     *   false: invalid input
     *   true: no errors
    """
    def writeSpeed(self, speed):
        # Check input limits
        if (speed < 0 or speed > 100):
            return True
        self.speed = speed
        # Write to PWM
        self.fan_controller.ChangeDutyCycle(self.speed)
        return False

    def setLimits(self, min, max):
        self.limit_min = min
        self.limit_max = max

    def autoSpeed(self, x):
        speed = map(constrain(x, self.limit_min, self.limit_max),
                    self.limit_min, self.limit_max,
                    0, 100)
        self.writeSpeed(speed)

    def readSpeed(self):
        """
         * Description
         *   .

         *   a_led.blink()


         * Parameters
         *   none


         * Returns
         *   false: if the last state was not modified
         *   true: if the last state was modified
        """
        return self.speed

    """
     * Description
     *   Get fan speed in RPM.

     *   fan.speedRPM()

     * Parameters
     *   none

     * Returns
     *   unsigned long: Fan speed in RPM
     *   unsigned long: -1 is errors found
    """
    def readRPM(self):
        return self.rpm

    """
    """
    def stop(self):
        return self.fan_controller.stop()

    """
    """
    def cleanup(self):
        self.stop()
        return GPIO.cleanup()


def constrain(x, a, b):
    """
    constrain(x, a, b)

    Description:
        Constrains a number to be within a range.

    Parameters:
        x: the number to constrain, all data types
        a: the lower end of the range, all data types
        b: the upper end of the range, all data types

    Returns:
        x: if x is between a and b
        a: if x is less than a
        b: if x is greater than b

    Original source:
        https://www.arduino.cc/en/Reference/Constrain
    """
    if x < a:
        return a
    elif b < x:
        return b
    else:
        return x


def map(x, in_min, in_max, out_min, out_max):
    """
    map(value, fromLow, fromHigh, toLow, toHigh)

    Description
        Re-maps a number from one range to another. That is, a value of fromLow
        would get mapped to toLow, a value of fromHigh to toHigh, values
        in-between to values in-between, etc.

        Does not constrain values to within the range, because out-of-range
        values are sometimes intended and useful. The constrain() function may
        be used either before or after this function, if limits to the ranges
        are desired.

        Note that the "lower bounds" of either range may be larger or smaller
        than the "upper bounds" so the map() function may be used to reverse a
        range of numbers, for example

        y = map(x, 1, 50, 50, 1);

        The function also handles negative numbers well, so that this example

        y = map(x, 1, 50, 50, -100);

        is also valid and works well.

        The map() function uses integer math so will not generate fractions,
        when the math might indicate that it should do so. Fractional remainders
        are truncated, and are not rounded or averaged.

    Parameters
        value: the number to map
        fromLow: the lower bound of the value's current range
        fromHigh: the upper bound of the value's current range
        toLow: the lower bound of the value's target range
        toHigh: the upper bound of the value's target range

    Returns
        The mapped value.

    Original source:
        https://www.arduino.cc/en/Reference/Map
    """
    x *= 1.0
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
