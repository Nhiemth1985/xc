"""
host.py

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log:
2019-07-08
        * Version: 0.04
        * Fixed: Verboseless messages.

2019-02-12
        * Version: 0.03
        * Fixed: Temperature sensing on Raspberry Pi.

2018-07-22
        * Version: 0.02b
        * Added: Suport to x86_64.

2018-06-30
        * Version: 0.01b
        * Added: First version.
"""

import sys
import json
import os
import platform
from psutil import virtual_memory
import re
from socket import gethostbyname
from tools.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, debug, debugln, code, codeln
from tools.timer import Timer

try:
    import RPi.GPIO as GPIO  # pylint: disable=import-error
    GPIO.setmode(GPIO.BOARD)
except BaseException:
    pass


class HostProperties:
    """
    description:
    """

    def __init__(self, data):
        self.version = 0.04
        self.load(data)
        self.set()

    def load(self, data):
        """
        description:
        """
        self.data = data

    def reset(self):
        """
        description:
        """
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
        self.fan_speed = None

    def set(self):
        """
        description:
        """
        self.reset()
        self.name = platform.node()
        self.machine = platform.machine()
        self.architecture = platform.architecture()[0]
        self.processor = platform.processor()
        self.core = os.sysconf("SC_NPROCESSORS_ONLN")
        self.memory = int(round(float(virtual_memory().total)/1024/1024/1024))
        self.memory_used = virtual_memory().percent
        self.system = platform.system()
        self.distribution = platform.linux_distribution()[0]
        self.distribution_version = platform.linux_distribution()[1]
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
        infoln("Host...")
        debugln("Profile: " + self.profile, 1)
        infoln("Name: " + self.name, 1)
        infoln("Machine: " + self.machine + " (" + self.architecture + ")", 1)
        debugln("Processor: " + self.processor, 1)
        debug("Core", 1)
        if self.core > 1:
            debug("s")
        debugln(": " + str(self.core))
        debugln("Memory: " +
                str(self.memory) + "GB (used: " +
                str(self.memory_used) + "%)", 1)
        debug("Operating system: " + self.system, 1)
        if platform.system() == 'Linux':
            debugln(" (" + self.distribution + " " +
                    self.distribution_version + ")")
        debugln("Python: " + self.python_version, 1)

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
        debugln('Temperature sensor: ' + status, 1)

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
                fan.autoSpeed(self.temperature)
                self.fan_speed = str("{:1.1f} RPM".
                                     format(float(self.fan.readRPM())))
        except BaseException:
            pass

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
                status += '    ' + str(fan_speed) + ' RPM'
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
            erroln("Could not load module. " + str(err))
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
        debugln('Temperature sensor: ' + status, 1)
        # Status LED
        status = 'Absent'
        try:
            if self.data[self.name]["resources"]["status_led"]:
                from xC.signal import SigGen
                GPIO.setup(33, GPIO.OUT)
                self.status_led = GPIO.PWM(33, 50)
                self.status_led.start(0)
                self.status_signal = SigGen()
                self.status_signal.period(1000)
                status = 'Present'
        except BaseException:
            pass
        infoln('Status LED: ' + status, 1)
        # Fan
        status = 'Absent'
        try:
            if self.data[self.name]["resources"]["fan"]:
                self.fan = Fan(32, 22, max_speed=2000)
                self.fan.setLimits(40, 60)
                self.fan_speed = 0
                status = 'Present'
        except BaseException:
            pass
        infoln('Fan: ' + status, 1)

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

    def stop_x86_64(self):
        """
        description:
        """
        pass

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