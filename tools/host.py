"""
---
name: host.py
description: Host package
copyright: 2018-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
  2019-09-07
  - version: 0.5
    fixed: Adequations to pyliny.
  2019-07-08
  - version: 0.04
    fixed: Verboseless messages.
  2019-02-12
  - version: 0.03
    fixed: Temperature sensing on Raspberry Pi.
  2018-07-22
  - version: 0.02b
    added: Suport to x86_64.
  2018-06-30
  - version: 0.01b
    added: First version.
"""

import sys
import os
import platform
import re
import distro
from psutil import virtual_memory
import tools.echo as echo
from tools.timer.timer import Timer

try:
    import RPi.GPIO as GPIO  # pylint: disable=import-error
    GPIO.setmode(GPIO.BOARD)
except BaseException:
    pass


class HostProperties:  # pylint: disable=too-many-instance-attributes
    """
    description:
    """

    def __init__(self, data):
        self.version = 0.5
        self.name = ''
        self.machine = ''
        self.architecture = ''
        self.processor = ''
        self.core = 0
        self.memory = 0
        self.memory_used = 0
        self.system = ''
        self.distribution = ''
        self.distribution_version = ''
        self.python_version = ''
        self.temperature = None
        self.status_led = None
        self.status_signal = None
        self.fan_speed = None
        self.fan = None
        self.timer = None
        self.load(data)
        self.set()

    def load(self, data):
        """
        description:
        """
        self.data = data

    def set(self):
        """
        description:
        """
        # self.reset()
        self.name = platform.node()
        self.machine = platform.machine()
        self.architecture = platform.architecture()[0]
        self.processor = platform.processor()
        self.core = os.sysconf("SC_NPROCESSORS_ONLN")
        self.memory = int(round(float(virtual_memory().total)/1024/1024/1024))
        self.memory_used = virtual_memory().percent
        self.system = platform.system()
        self.distribution = distro.linux_distribution()[0]
        self.distribution_version = distro.linux_distribution()[1]
        self.python_version = platform.python_version()
        self.profile = 'generic'
        if self.name in self.data:
            self.profile = self.name
        else:
            self.profile = 'generic'

    def info(self):
        """
        description:
        """
        echo.infoln("Host...")
        echo.debugln("Profile: " + self.profile, 1)
        echo.infoln("Name: " + self.name, 1)
        echo.debugln("Machine: " + self.machine + " (" + self.architecture + ")", 1)
        echo.debugln("Processor: " + self.processor, 1)
        echo.debug("Core", 1)
        if self.core > 1:
            echo.debug("s")
        echo.debugln(": " + str(self.core))
        echo.debugln("Memory: " +
                     str(self.memory) + "GB (used: " +
                     str(self.memory_used) + "%)", 1)
        echo.debug("Operating system: " + self.system, 1)
        if platform.system() == 'Linux':
            echo.debugln(" (" + self.distribution + " " +
                         self.distribution_version + ")")
        echo.debugln("Python: " + self.python_version, 1)

    def run(self):
        """
        description:
        """
        if self.machine == 'armv7l':
            self.run_armv7l()
        if self.machine == 'x86_64':
            self.run_x86_64()

    def start_x86_64(self):
        """
        description:
        """
        self.timer = Timer(1000)
        # Temperature sensor
        status = 'Absent'
        try:
            if self.data[self.name]["resources"]["temperature_sensor"]:
                self.temperature = 0
                status = 'Present'
        except BaseException:
            pass
        echo.debugln('Temperature sensor: ' + status, 1)

    def start(self):
        """
        description:
        """
        if self.machine == 'armv7l':
            self.start_armv7l()
        if self.machine == 'x86_64':
            self.start_x86_64()

    def run_x86_64(self):
        """
        description:
        """
        if not self.timer.check():
            return False
        # Temperature sensor
        try:
            if self.data[self.name]["resources"]["temperature_sensor"]:
                from psutil import sensors_temperatures
                payload = str(sensors_temperatures()['acpitz']).split(',')[1]
                temperature = re.sub(r' [a-z]*=', '', payload)
                self.temperature = str("{:1.0f} C".
                                       format(float(temperature)))
        except BaseException:
            pass
        return False

    def run_armv7l(self):
        """
        description:
        """
        # Blink Status LED
        try:
            if self.data[self.name]["resources"]["status_led"]:
                self.status_led.ChangeDutyCycle(self.status_signal.sine() * 100)
        except BaseException:
            pass
        # Check sensors
        if not self.timer.check():
            return False
        # Temperature sensor
        try:
            if self.data[self.name]["resources"]["temperature_sensor"]:
                temp = os.popen("vcgencmd measure_temp").readline()
                temp = temp.replace("temp=", "")
                temp = temp.replace("\'C", "")
                self.temperature = str("{:1.0f} C".format(float(temp)))
        except BaseException:
            pass
        # Fan speed
        try:
            if self.data[self.name]["resources"]["temperature_sensor"] and \
               self.data[self.name]["resources"]["fan"]:
                self.fan.auto_speed(self.temperature)
                self.fan_speed = str("{:1.1f} RPM".
                                     format(float(self.fan.read_rpm())))
        except BaseException:
            pass
        return False

    def status_armv7l(self):
        """
        description:
        """
        status = ''
        self.run_armv7l()
        try:
            if self.data[self.name]["resources"]["temperature_sensor"]:
                status = self.temperature
        except BaseException:
            pass
        try:
            if self.data[self.name]["resources"]["temperature_sensor"] and \
               self.data[self.name]["resources"]["fan"]:
                status += '    ' + str(self.fan_speed) + ' RPM'
        except BaseException:
            pass
        return status

    def status_x86_64(self):
        """
        description:
        """
        status = ''
        self.run_x86_64()
        try:
            if self.data[self.name]["resources"]["temperature_sensor"]:
                status = self.temperature
        except BaseException:
            pass
        return status

    def status(self):
        """
        description:
        """
        if self.machine == 'armv7l':
            return self.status_armv7l()
        if self.machine == 'x86_64':
            return self.status_x86_64()
        return ''

    def start_armv7l(self):
        """
        description:
        """
        try:
            from fan import Fan
        except ImportError as err:
            echo.erroln("Could not load module. " + str(err))
            sys.exit(True)
        self.timer = Timer(1000)
        # Temperature sensor
        status = 'Absent'
        try:
            if self.data[self.name]["resources"]["temperature_sensor"]:
                self.temperature = 0
                status = 'Present'
        except BaseException:
            pass
        echo.debugln('Temperature sensor: ' + status, 1)
        # Status LED
        status = 'Absent'
        try:
            if self.data[self.name]["resources"]["status_led"]:
                from tools.signal import SigGen
                GPIO.setup(33, GPIO.OUT)
                self.status_led = GPIO.PWM(33, 50)
                self.status_led.start(0)
                self.status_signal = SigGen()
                self.status_signal.period(1000)
                status = 'Present'
        except BaseException:
            pass
        echo.infoln('Status LED: ' + status, 1)
        # Fan
        status = 'Absent'
        try:
            if self.data[self.name]["resources"]["fan"]:
                self.fan = Fan(32, 22, max_speed=2000)
                self.fan.set_limits(40, 60)
                self.fan_speed = 0
                status = 'Present'
        except BaseException:
            pass
        echo.infoln('Fan: ' + status, 1)

    def get_control(self):
        """
        description:
        """
        try:
            return self.data[self.name]["control"]
        except BaseException:
            pass

    def get_screen(self):
        """
        description:
        """
        try:
            return self.data[self.name]["screen"]
        except BaseException:
            pass

    def get_screensaver(self):
        """
        description:
        """
        try:
            return self.data[self.name]["screensaver"]
        except BaseException:
            pass

    def stop(self):
        """
        description:
        """
        if self.machine == 'armv7l':
            self.stop_armv7l()
        if self.machine == 'x86_64':
            self.stop_x86_64()

    def stop_x86_64(self):  # pylint: disable=no-self-use
        """
        description:
        """
        return False

    def stop_armv7l(self):
        """
        description:
        """
        try:
            if self.data[self.name]["resources"]["status_led"]:
                self.status_led.stop()
        except BaseException:
            pass
        try:
            if self.data[self.name]["resources"]["fan"]:
                self.fan.stop()
        except BaseException:
            pass
        try:
            if self.data[self.name]["resources"]["status_led"] or \
               self.data[self.name]["resources"]["fan"]:
                GPIO.cleanup()
        except BaseException:
            pass
