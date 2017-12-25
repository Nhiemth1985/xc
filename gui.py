"""
gui.py

Author: Marcio Pessoa <marcio@pessoa.eti.br>
Contributors: none

Change log:
2017-07-27
        * Version: 0.13b
        * Improvement: Added memory information to startup messages.

2017-07-20
        * Version: 0.12b
        * Improvement: Removed function map().
        * Improvement: Removed function constrain().

2017-06-26
        * Version: 0.11b
        * New feature: Hardware startup messages.
        * New feature: Added Status LED control.
        * New feature: Added temperature sensor.
        * New feature: Added fan control and fan speed sensor.
        * New feature: Hardware information for Raspberry Pi .
        * Improvement: Added function map().
        * Improvement: Added function constrain().

2017-06-13
        * Version: 0.10b
        * Improvement: Detailed control start messages.

2017-05-22
        * Version: 0.09b
        * New feature: Keyboard and mouse detection.

2017-05-19
        * Version: 0.08b
        * New feature: Joystick buttons support.

2017-05-17
        * Version: 0.07b
        * Bug fix: Correction applied to joystick precision.
        * Improvement: Added mouse speed configuration.
        * Improvement: Added joystick speed configuration.

2017-05-12
        * Version: 0.06b
        * New feature: Joystick support.
        * Improvement: Unified object drawing.

2017-05-11
        * Version: 0.05b
        * New feature: Mouse support.

2017-05-10
        * Version: 0.04b
        * New feature: Automatically build object from JSON definition.
        * New feature: Keyboard support.

2017-05-08
        * Version: 0.03b
        * Improvement: Check for TrueType fonts on start up.
        * Improvement: Removed __presentation() method.

2017-04-04
        * Version: 0.02b
        * New feature: Added Image class to manage images easily.

2017-04-01
        * Version: 0.01b
        * Improvement: Added version information.

2016-05-12
        * Version: 0.00b
        * Scrach version.

"""

import os.path
import os
import platform
import pygame
from psutil import virtual_memory
from pygame.locals import *
import serial
import subprocess
import sys
import time
from command_parser import CommandParser
from device_properties import DeviceProperties
from devtools import DevTools
from echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln
from signal_generator import SigGen
from timer import Timer

if platform.machine() == 'armv7l':
    try:
        import RPi.GPIO as GPIO
        from gpiozero import CPUTemperature
        from fan import Fan
    except ImportError as err:
        print("Could not load module. " + str(err))
        sys.exit(True)

REFRESH_RATE = 60  # Frames per second

xc_path = os.getenv('XC_PATH', '/opt/sciemon/xc')
images_directory = os.path.join(xc_path, 'images')


class Gui:
    """  """

    def __init__(self):
        self.version = '0.13b'
        self.window_title = 'xC'
        self.window_caption = 'xC - Axes Controller'
        self.fullscreen = False
        self.id = None
        self.interface = 'serial'
        self.config_file = None
        self.is_connected = False
        self.is_ready = False
        self.check_device_timer = Timer(1000)
        self.fan_speed = None
        self.temperature = None

    def ctrl_joystick_end(self):
        pygame.joystick.quit()

    def ctrl_joystick_handle(self, event):
        if self.control_joystick_enable is not True:
            return
        if (event.type == JOYBUTTONDOWN or event.type == JOYBUTTONUP):
            for i in self.device.objects():
                try:
                    i["control"]["joystick"]
                except:
                    continue
                if i["control"]["joystick"].split("[")[0] == "button":
                    button = []
                    for j in range(self.joystick.get_numbuttons()):
                        button.append(self.joystick.get_button(j))
                        # infoln("button[" + str(j) + "] = " + str(button[j]))
                    if eval(i["control"]["joystick"]):
                        if i["type"] == "push-button":
                            i["state"] = i["on"]["picture"]
                            command = i["on"]["command"]
                            if self.is_connected:
                                self.session.send_wait(command)
                        if i["type"] == "switch":
                            state = True if i["state"] == "on" else False
                            state = not state
                            i["state"] = "on" if state else "off"
                            # infoln("b[" + str(j) + "] state = " + i["state"])
                            command = i[i["state"]]["command"]
                            if self.is_connected:
                                self.session.send_wait(command)
        if (event.type == JOYHATMOTION or self.joystick_hat_active):
            for i in self.device.objects():
                try:
                    i["control"]["joystick"]
                except:
                    continue
                if i["control"]["joystick"].split("[")[0] == "hat":
                    hat = []
                    for j in range(self.joystick.get_numhats()):
                        hat.append(self.joystick.get_hat(j))
                        # infoln("hat[" + str(j) + "] = " + str(hat[j]))
                    if 1 in hat[0] or -1 in hat[0]:
                        self.joystick_hat_active = True
                    else:
                        self.joystick_hat_active = False
                    if eval(i["control"]["joystick"]):
                        i["state"] = i["on"]["picture"]
                        if self.is_connected:
                            n = 1
                            command = i["on"]["command"].replace('*', str(n))
                            self.session.send_wait(command)
                    else:
                        i["state"] = i["off"]["picture"]
        if event.type == JOYAXISMOTION:
            if self.joystick_timer.check() is not True:
                return
            # Search for configured axes
            for i in self.device.objects():
                try:
                    i["control"]["joystick"]
                except:
                    continue
                if event.type == pygame.JOYAXISMOTION and \
                   i["control"]["joystick"].split("[")[0] == "axis":
                    axis = []
                    for j in range(self.joystick.get_numaxes()):
                        axis.append(self.joystick.get_axis(j))
                        # infoln("axis[" + str(j) + "] = " + str(axis[j]))
                    if eval(i["control"]["joystick"]):
                        i["state"] = i["on"]["picture"]
                        if self.is_connected:
                            # Get joystick axis number from JSON device file and
                            # atrib axis[?] value to n variable
                            n = eval(i["control"]["joystick"].split(" ")[0])
                            n = abs(n * self.control_joystick_speed)
                            n = int(round(n))
                            if int(n) == 0:
                                continue
                            command = i["on"]["command"].replace('*', str(n))
                            self.session.send_wait(command)
                    else:
                        i["state"] = i["off"]["picture"]

    def ctrl_joystick_start(self):
        info('    Joystick: ')
        # Is enable?
        try:
            self.control_joystick_enable = (self.device.control()
                                            ["joystick"]["enable"])
        except:
            self.control_joystick_enable = False
        # Is speed configured?
        try:
            self.control_joystick_speed = (self.device.control()
                                           ["joystick"]["speed"])
        except:
            self.control_joystick_speed = 1
        # Draw
        self.joyicon = Image(self.background,
                             os.path.join(images_directory, 'joystick.png'),
                             [2, 1])
        self.joyicon.draw([self.control_joystick_enable, 0], [20, 200])
        self.joystick_hat_active = False
        # Detect and start
        joysticks = pygame.joystick.get_count()
        if joysticks:
            infoln(str(joysticks))
            for i in range(joysticks):
                self.joystick = pygame.joystick.Joystick(i)
                self.joystick.init()
                try:
                    delay = self.device.control()["joystick"]["delay"]
                except:
                    delay = 100
                self.joystick_timer = Timer(delay)
                infoln('        ' + self.joystick.get_name())
                infoln('            Axes: ' + str(self.joystick.get_numaxes()))
                infoln('            Buttons: ' +
                       str(self.joystick.get_numbuttons()))
                infoln('            Balls: ' +
                       str(self.joystick.get_numballs()))
                infoln('            Hats: ' + str(self.joystick.get_numhats()))
                infoln('            Speed: ' +
                       str(self.control_joystick_speed) + '%')
                infoln('            Delay: ' + str(delay) + 'ms')
        else:
            infoln('None')

    def ctrl_keyboard_end(self):
        pass

    def ctrl_keyboard_handle(self, event):
        # Program behavior
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:  # Escape
                self.running = False
            if event.key == K_F1:  # Help screen
                help_screen_on = True
            if event.key == K_F8:  # Keyboard grab
                self.control_keyboard_enable = \
                    not self.control_keyboard_enable
                self.keyboard.draw([self.control_keyboard_enable, 0])
            if event.key == K_F9:  # Mouse grab
                self.control_mouse_enable = \
                    not self.control_mouse_enable
                pygame.mouse.set_visible(not self.control_mouse_enable)
                pygame.event.set_grab(self.control_mouse_enable)
                self.mouse.draw([self.control_mouse_enable, 0])
            if event.key == K_F10:  # Joystick grab
                self.control_joystick_enable = \
                    not self.control_joystick_enable
                self.joyicon.draw([self.control_joystick_enable, 0])
            if event.key == K_F11:  # Touch grab
                self.control_touch_enable = \
                    not self.control_touch_enable
                self.touch.draw([self.control_touch_enable, 0])
            if event.key == K_F12:  # Voice grab
                self.control_voice_enable = \
                    not self.control_voice_enable
                self.voice.draw([self.control_voice_enable, 0])
            if event.key == K_LALT:  # Release controls
                self.control_keyboard_enable = False
                self.control_mouse_enable = False
                self.control_joystick_enable = False
                self.control_touch_enable = False
                self.control_voice_enable = False
                pygame.mouse.set_visible(not self.control_mouse_enable)
                pygame.event.set_grab(self.control_mouse_enable)
                self.keyboard.draw([0, 0])
                self.mouse.draw([0, 0])
                self.joyicon.draw([0, 0])
                self.touch.draw([0, 0])
                self.voice.draw([0, 0])
        # Object behavior
        if self.control_keyboard_enable is False:
            return
        for i in self.device.objects():
            try:
                i["control"]["keyboard"]
            except:
                continue
            if i["type"] == "push-button":
                if event.type == KEYDOWN and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["state"] = i["on"]["picture"]
                    if self.is_connected:
                        command = i["on"]["command"].replace('*', '1')
                        self.session.send_wait(command)
                if event.type == KEYUP and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["state"] = i["off"]["picture"]
            if i["type"] == "switch":
                if event.type == KEYDOWN and \
                   event.key == eval(i["control"]["keyboard"]):
                    state = True if i["state"] == "on" else False
                    state = not state
                    i["state"] = "on" if state else "off"
                    if self.is_connected:
                        command = i[i["state"]]["command"].replace('*', '1')
                        self.session.send_wait(command)
                if event.type == KEYUP and \
                   event.key == eval(i["control"]["keyboard"]):
                    pass

    def ctrl_keyboard_start(self):
        info('    Keyboard: ')
        # Is enable?
        try:
            self.control_keyboard_enable = (self.device.control()
                                            ["keyboard"]["enable"])
        except:
            self.control_keyboard_enable = False
        # Is speed configured?
        try:
            self.control_keyboard_speed = (self.device.control()
                                           ["keyboard"]["speed"])
        except:
            self.control_keyboard_speed = 1
        # Is delay configured?
        try:
            self.control_keyboard_delay = (self.device.control()
                                           ["keyboard"]["delay"])
        except:
            self.control_keyboard_delay = 1
        # Draw
        self.keyboard = Image(self.background,
                              os.path.join(images_directory, 'keyboard.png'),
                              [2, 1])
        self.keyboard.draw([self.control_keyboard_enable, 0], [20, 100])
        # Check for device
        check_input = os.path.join(xc_path, 'scripts/check_input.sh')
        cmd = [check_input, 'keyboard']
        null = open(os.devnull, 'w')
        return_code = subprocess.call(cmd)
        if return_code == 0:
            infoln('Found')
            infoln('        ' + 'Speed: ' + str(self.control_keyboard_speed) +
                   'ms')
            infoln('        ' + 'Delay: ' + str(self.control_keyboard_delay) +
                   'ms')
        else:
            infoln('None')
        pygame.key.set_repeat(1, 100)

    def ctrl_mouse_end(self):
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def ctrl_mouse_handle(self, event):
        if self.control_mouse_enable is False:
            return
        if event.type == MOUSEMOTION:
            # Get relativa mouse position
            r = pygame.mouse.get_rel()
            x = r[0]
            y = r[1]
            if x == 0 and y == 0:
                return
            #
            for i in self.device.objects():
                try:
                    i["control"]["mouse"]
                except:
                    continue
                if eval(i["control"]["mouse"]):
                    i["state"] = i["on"]["picture"]
                    if self.is_connected:
                        try:
                            # infoln("Position = " + str(r))
                            # Get joystick axis number from JSON device file and
                            # atrib axis[?] value to n variable
                            n = eval(i["control"]["mouse"].split(" ")[0])
                            n = abs(n * self.control_mouse_speed)
                            n = int(round(n))
                            if int(n) == 0:
                                continue
                            command = i["on"]["command"].replace('*', str(n))
                            self.session.send_wait(command)
                        except:
                            pass
                else:
                    i["state"] = i["off"]["picture"]

    def ctrl_mouse_start(self):
        info('    Mouse: ')
        # Is enable?
        try:
            self.control_mouse_enable = (self.device.control()
                                         ["mouse"]["enable"])
        except:
            self.control_mouse_enable = False
        # Is speed configured?
        try:
            self.control_mouse_speed = (self.device.control()
                                        ["mouse"]["speed"])
        except:
            self.control_mouse_speed = 1
        # Draw
        self.mouse = Image(self.background,
                           os.path.join(images_directory, 'mouse.png'),
                           [2, 1])
        self.mouse.draw([self.control_mouse_enable, 0], [20, 150])
        # Check for device
        check_input = os.path.join(xc_path, 'scripts/check_input.sh')
        cmd = [check_input, 'mouse']
        null = open(os.devnull, 'w')
        return_code = subprocess.call(cmd)
        if return_code == 0:
            infoln('Found')
            infoln('        ' + 'Speed: ' + str(self.control_mouse_speed) + '%')
            pygame.mouse.set_visible(not self.control_mouse_enable)
            pygame.event.set_grab(self.control_mouse_enable)
        else:
            infoln('None')

    def ctrl_touch_end(self):
        pass

    def ctrl_touch_handle(self, event):
        if self.control_touch_enable is False:
            return

    def ctrl_voice_end(self):
        pass

    def ctrl_touch_start(self):
        info('    Touch: ')
        self.touch = Image(self.background,
                           os.path.join(images_directory, 'touch.png'),
                           [2, 1])
        self.touch.draw([0, 0], [20, 250])
        infoln('Not implemented yet.')
        self.control_touch_enable = False

    def ctrl_voice_handle(self, event):
        if self.control_voice_enable is False:
            return

    def ctrl_voice_start(self):
        info('    Voice: ')
        self.voice = Image(self.background,
                           os.path.join(images_directory, 'voice.png'),
                           [2, 1])
        self.voice.draw([0, 0], [20, 300])
        infoln('Not implemented yet.')
        self.control_voice_enable = False

    def device_check(self):
        if not self.check_device_timer.check():
            return
        self.is_connected = self.device.is_serial_connected()
        if (self.is_connected is False) and (self.is_ready is True):
            self.id = None
            self.interface = 'serial'
            self.is_ready = False
            self.start()
        if self.is_connected is False:
            if self.device.detect():
                self.start()

    def device_connect(self, id=None, interface=None):
        # Select device
        if id:
            self.id = id
            self.device.select(self.id)
        else:
            if self.device.select_auto():
                self.device.presentation()
            else:
                return False
        # Connect to device
        if interface:
            self.interface = interface
            self.window_title = self.device.system_plat + ' Mark ' + \
                self.device.system_mark
            self.window_caption = self.device.system_plat + ' Mark ' + \
                self.device.system_mark + ' - ' + \
                self.device.system_desc
            infoln("Connecting...")
            if self.interface == 'serial':
                self.is_connected = self.device.is_serial_connected()
                if self.is_connected:
                    try:
                        time.sleep(self.device.startup()["delay"] / 1000)
                        session = serial.Serial(self.device.comm_serial_path,
                                                self.device.comm_serial_speed,
                                                timeout=1)
                        self.session = CommandParser(session)
                        return False
                    except:
                        return True
                else:
                    erroln('Device is not connected.')
                    infoln('Try again after connecting the device: ' +
                           str(self.device.comm_serial_path))
                    self.is_connected = False
                    return True
            elif self.interface == 'network':
                if self.device.comm_network_address is None:
                    erroln("Interface not configured for this device.")
                    self.is_connected = False
                    return True
                if not self.device.is_network_connected():
                    erroln('Device is not reacheable: ' +
                           str(self.device.comm_network_address))
                    self.is_connected = False
                    return True

    def device_draw(self):
        # Device name
        font = pygame.font.SysFont('Ubuntu', 22)
        text = font.render(self.window_caption, True, (100, 100, 100))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        textpos[1] += 10
        self.screen.blit(text, textpos)

    def device_start(self):
        if self.is_connected:
            while not self.is_ready:
                self.is_ready = self.session.is_ready()
            for c in self.device.startup()["command"]:
                self.session.send(c)
                self.session.receive()

    def end(self):
        self.ctrl_joystick_end()
        self.ctrl_keyboard_end()
        self.ctrl_mouse_end()
        self.ctrl_touch_end()
        self.ctrl_voice_end()
        pygame.quit()
        # Stop Raspberry Pi resources
        if platform.machine() == 'armv7l':
            # Status LED
            self.status_led.stop()
            # Cooling system
            self.fan.stop()
            # Terminal GPIO interface
            GPIO.cleanup()

    def images_load(self):
        # Help screen
        self.helpscreen = Image(self.screen,
                                os.path.join(images_directory, 'help.png'))
        imgpos = self.helpscreen.surface.get_rect()
        imgpos.center = self.background.get_rect().center
        self.helpscreen.position(position=imgpos)

    def object_build(self):
        for i in self.device.objects():
            i["id"] = Image(self.screen,
                            os.path.join(images_directory,
                                         i["picture"]["file"]),
                            eval(i["picture"]["split"]))
            i["id"].draw(eval(i["picture"][i["default"]]),
                         eval(i["picture"]["position"]))
            i["state"] = i["default"]

    def object_draw(self):
        for i in self.device.objects():
            i["id"].draw(eval(i["picture"][i["state"]]))

    def run(self):
        infoln('Ready...')
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.ctrl_keyboard_handle(event)
                self.ctrl_mouse_handle(event)
                self.ctrl_joystick_handle(event)
                self.ctrl_touch_handle(event)
                self.ctrl_voice_handle(event)
            self.screen_draw()
            self.device_check()
        infoln("Exiting...")
        self.end()
        return False

    def screen_draw(self):
        self.screen.blit(self.background, (0, 0))
        self.object_draw()
        self.status_draw()
        self.device_draw()
        self.clock.tick(REFRESH_RATE)
        pygame.display.flip()

    def start(self, screen_size):
        global pygame

        self.screen_resolution = (800, 600)  # pixels (default resolution)
        if screen_size == 'Full':
            self.fullscreen = True
        else:
            self.screen_resolution = map(int, screen_size.split('x'))
            

        # Set computer architechture
        infoln("Current system...")
        infoln("    Name: " + platform.node())
        infoln("    Processor: " + platform.processor())
        infoln("    Machine: " + platform.machine() + " (" +
               platform.architecture()[0] + ")")
        infoln("    Memory: " +
               str(int(round(float(virtual_memory().total)/1024/1024/1024))) +
               "GB (used: " +
               str(virtual_memory().percent) +
               "%)")
        info("    Operating system: " + platform.system())
        if platform.system() == 'Linux':
            infoln(" (" + platform.linux_distribution()[0] + " " +
                   platform.linux_distribution()[1] + ")")
        infoln("    Python: " + platform.python_version())

        # Initialize Raspberry Pi resources
        if platform.machine() == 'armv7l':
            # Initialize GPIO interface
            GPIO.setmode(GPIO.BOARD)
            # Status LED
            GPIO.setup(33, GPIO.OUT)
            self.status_led = GPIO.PWM(33, 50)
            self.status_led.start(0)
            self.status_signal = SigGen()
            self.status_signal.period(1000)
            # Cooling system
            self.temperature_timer = Timer(1000)
            self.temperature = 0
            self.fan = Fan(32, 22, max_speed=2000)
            self.fan.setLimits(40, 60)

        # Load device configuration file
        self.device = DeviceProperties(self.config_file)

        # Connect to device
        self.device_connect(self.id, self.interface)

        # Starting screen
        infoln("Starting screen...")
        infoln("    Size: " + str(self.screen_resolution[0]) + 'x' +
               str(self.screen_resolution[1]))
        infoln("    Refresh rate: " + str(REFRESH_RATE) + ' FPS')
        # Positioning
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        # os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (200, 200)
        # Initialise screen
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_resolution, RESIZABLE)
        if self.fullscreen:
            pygame.display.toggle_fullscreen()
        # Define window caption
        # pygame.display.set_caption(self.window_caption)
        pygame.display.set_caption(self.window_title)
        # Checking fonts
        infoln('    Checking fonts...')
        for ttf_name in ['Digital Readout Thick Upright',
                         'Ubuntu']:
            ttf_path = pygame.font.match_font(ttf_name)
            if ttf_path is None:
                erroln('TrueType font missing.')
                infoln('        \"' + ttf_name + '\" not found (' +
                       ttf_path + ')')
        # Fill background
        self.background = pygame.Surface(self.screen.get_size())
        # self.background = self.background.convert()
        # self.background.fill([0, 0, 0])  # Black
        # Load images
        infoln('    Loading images...')
        try:
            file = os.path.join(images_directory, 'background.png')
            self.background_image = pygame.image.load(file)
            self.background = pygame.Surface(self.screen.get_size())
            self.background.blit(self.background_image, [0, 0])
        except pygame.error:
            raise SystemExit('Could not load image "%s" %s' %
                             (file, pygame.get_error()))
        self.images_load()
        # Building device objects
        infoln('    Building device objects...')
        self.object_build()
        # Clockling
        infoln('    Clockling...')
        self.clock = pygame.time.Clock()
        infoln('    Drawing...')
        self.screen_draw()

        infoln('Checking for input methods...')
        self.ctrl_keyboard_start()
        self.ctrl_mouse_start()
        self.ctrl_joystick_start()
        self.ctrl_touch_start()
        self.ctrl_voice_start()

        infoln('Starting device...')
        self.device_start()

    def status_draw(self):
        # Frame rate
        fps = str("FPS: {:1.1f}".format(float(self.clock.get_fps())))
        font = pygame.font.SysFont("Digital Readout Thick Upright", 13)
        text = font.render(fps, True, (32, 128, 32))
        textpos = text.get_rect()
        textpos.bottomleft = self.background.get_rect().bottomleft
        textpos[0] += 3
        textpos[1] += -2
        self.screen.blit(text, textpos)

        # Device connection status
        connection = 'Connected' if self.device.is_serial_connected() \
                     else 'Disconnected'
        font = pygame.font.SysFont("Digital Readout Thick Upright", 13)
        text = font.render(connection, True, (32, 128, 32))
        textpos = text.get_rect()
        textpos.bottomright = self.background.get_rect().bottomright
        textpos[0] += -3
        textpos[1] += -2
        self.screen.blit(text, textpos)

        # Run Raspberry Pi resources
        if platform.machine() == 'armv7l':
            # Blink Status LED
            self.status_led.ChangeDutyCycle(self.status_signal.sine() * 100)
            # Cooling system
            if self.temperature_timer.check():
                self.temperature = CPUTemperature().temperature
                self.fan.autoSpeed(self.temperature)
                self.fan_speed = self.fan.readRPM()

        # Fan speed
        if self.fan_speed is None:
            return False
        tmp = str("Temperature: {:1.0f} C".format(float(self.temperature)))
        rpm = str("Fan: {:1.0f} RPM".format(float(self.fan_speed)))
        font = pygame.font.SysFont("Digital Readout Thick Upright", 13)
        text = font.render(tmp + "          " + rpm, True, (32, 128, 32))
        textpos = text.get_rect()
        textpos.midbottom = self.background.get_rect().midbottom
        self.screen.blit(text, textpos)

    def terminal(self):
        self.terminal = pygame.Surface((320, 200))
        font = pygame.font.SysFont('Ubuntu', 14)
        text = font.render(self.window_caption, True, (131, 148, 150))
        textpos = text.get_rect()
        textpos.bottomleft = self.background.get_rect().bottomleft
        textpos[1] += 10
        self.terminal.blit(text, textpos)


class Image:
    """  """
    def __init__(self, screen, source, splits=[None, None]):
        self.source = source
        self.screen = screen
        self.surface = pygame.image.load(self.source)
        self.size = self.surface.get_rect().size
        self.splits = splits
        if self.splits != [None, None]:
            self.split(self.splits)

    def draw(self, item=[None, None], position=[None, None]):
        if position != [None, None]:
            self.position = position
        if item == [None, None]:
            self.screen.blit(self.surface, self.position)
        else:
            if item[0] > (self.splits[0] - 1) or \
               item[1] > (self.splits[1] - 1):
                warnln('Split image out of range: ' + self.source)
            self.screen.blit(self.surface, self.position, self.piece(item))

    def piece(self, item):
        """
        Description:
            Define one piece points of an image.

        Example:
            Consider a single image, split it into 8 equal pieces, like
            this:
                ╭───┬───┬───┬───╮
                │ 1 │ 2 │ 3 │ 4 │
                ├───┼───┼───┼───┤
                │ 5 │ 6 │ 7 │ 8 │
                ╰───┴───┴───┴───╯

            Take a look at one piece, the piece number 7 for example:
               A╭───╮B
                │ 7 │
               D╰───╯C

            All pieces have 4 sides and 4 corners. Each corner can be
            identified by A, B, C and D.
            To define a sub area of an image, you must have just A and C
            corner.

            I wrote the following code with A and C in lower case to adopt
            PEP 0008 -- Style Guide for Python Code.

        Parameters:
            A list with x and y piece of image.

        Returns:
            A list with x and y coodinates of piece of image.
        """
        a = [0, 0]
        c = [0, 0]
        a[0] = self.dimensions[0] * item[0]
        a[1] = self.dimensions[1] * item[1]
        c[0] = self.dimensions[0]
        c[1] = self.dimensions[1]
        return [a, c]

    def position(self, position):
        self.position = position

    def split(self, splits):
        self.dimensions = [0, 0]
        self.splits = splits
        self.splits_total = self.splits[0] * self.splits[1]
        self.dimensions[0] = self.size[0] / self.splits[0]
        self.dimensions[1] = self.size[1] / self.splits[1]
        return self.splits_total
