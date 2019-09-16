"""
---
name: fan.py
description: Fan controller
copyright: 2017-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
  2019-09-07
  - version: 0.3
    fixed: pylint friendly.
  2017-07-20
  - version: 0.02b
    added: Method set_limits() to pre define temperature limits.
    added: Method auto_speed()
    added: function amap().
    added: function constrain().
  2017-06-27
  - version: 0.01b
    fixed: Some minor fixes.
  2017-06-25
  - version: 0.00b
    added: First version.
"""

import RPi.GPIO as GPIO  # pylint: disable=import-error, useless-import-alias
from tools.pytimer.pytimer import Timer


class Fan():  # pylint: disable=too-many-instance-attributes
    """
    description: Fan speed control.

        Fan (write_pin, read_pin)

    parameters:
        write_pin: Arduino LED connected to PWM motor controller
        read_pin: Arduino pin connected to motor sensor pin

    returns:
        void
    """

    def __init__(self, write_pin, read_pin=None, max_speed=3000):
        self.version = 0.3
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
        #               Raspberry Pis Broadcom-chip brain.
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

    def counter(self):
        """
        description: Just a counter.

        parameters:
            none

        returns:
            bool
        """
        if not self.is_sensor_present:
            self.counter_rpm = 0
            return True
        # Count
        self.counter_rpm += 1
        if self.timer.check():
            self.rpm = int(self.counter_rpm / self.delta_t * 1000 * 60 / 2.0)
            self.counter_rpm = 0
        return False

    def write_speed(self, speed):
        """
        description: Change fan speed value.

            fan.speedWrite(int percent_speed)

        parameters:
            percent_speed: Fan percent speed

        returns:
            false: invalid input
            true: no errors
        """
        # Check input limits
        if (speed < 0 or speed > 100):
            return True
        self.speed = speed
        # Write to PWM
        self.fan_controller.ChangeDutyCycle(self.speed)
        return False

    def set_limits(self, minimum, maximum):
        """
        description:
        """
        self.limit_min = minimum
        self.limit_max = maximum

    def auto_speed(self, x_input):
        """
        description:
        """
        speed = amap(constrain(x_input, self.limit_min, self.limit_max),
                     self.limit_min, self.limit_max,
                     0, 100)
        self.write_speed(speed)

    def read_speed(self):
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

    def read_rpm(self):
        """
        description:
        """
        return self.rpm

    def stop(self):
        """
        description:
        """
        return self.fan_controller.stop()


    def cleanup(self):
        """
        description:
        """
        self.stop()
        return GPIO.cleanup()


def constrain(number_x, number_a, number_b):
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
    if number_x < number_a:
        return number_a
    if number_b < number_x:
        return number_b
    return number_x


def amap(x_input, in_min, in_max, out_min, out_max):
    """
    description:
        Re-maps a number from one range to another. That is, a value of in_min
        would get mapped to out_min, a value of in_max to out_max, values
        in-between to values in-between, etc.

        Note that the "lower bounds" of either range may be larger or smaller
        than the "upper bounds" so the amap() function may be used to reverse a
        range of numbers, for example:

        y = amap(x, 1, 50, 50, 1);

        The function also handles negative numbers well, so that this example

        y = amap(x, 1, 50, 50, -100);

        is also valid and works well.

    usage:
        amap(value, in_min, in_max, out_min, out_max)

    parameters:
        value: the number to map
        in_min: the lower bound of the value's current range
        in_max: the upper bound of the value's current range
        out_min: the lower bound of the value's target range
        out_max: the upper bound of the value's target range

    returns:
        The mapped value.

    reference:
        https://www.arduino.cc/en/Reference/Map
    """
    # x_input *= 1.0
    return (x_input - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
