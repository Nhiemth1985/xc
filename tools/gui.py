"""
---
name: gui.py
description: Graphical User Interface
copyright: 2016-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  contributors:
  - name: None
change-log:
  2019-07-08
  - version: 0.19
    fixed: Verboseless messages.
  2019-01-01
  - version: 0.18
    changed: Python 3 ready.
  2018-06-27
  - version: 0.17b
    changed: Removed resizeable window feature.
  2018-06-19
  - version: 0.16b
    added: Pong easter egg
  2018-06-05
  - version: 0.15b
    added: CPU Core number.
  2018-01-27
  - version: 0.14b
    added: Screen resolution customization.
  2017-07-27
  - version: 0.13b
    improvement: Added memory information to startup messages.
  2017-07-20
  - version: 0.12b
    improvement: Removed function map().
    improvement: Removed function constrain().
  2017-06-26
  - version: 0.11b
    added: Hardware startup messages.
    added: Added Status LED control.
    added: Added temperature sensor.
    added: Added fan control and fan speed sensor.
    added: Hardware information for Raspberry Pi .
    improvement: Added function map().
    improvement: Added function constrain().
  2017-06-13
  - version: 0.10b
    improvement: Detailed control start messages.
  2017-05-22
  - version: 0.09b
    added: Keyboard and mouse detection.
  2017-05-19
  - version: 0.08b
    added: Joystick buttons support.
  2017-05-17
  - version: 0.07b
    fixed: Correction applied to joystick precision.
    improvement: Added mouse speed configuration.
    improvement: Added joystick speed configuration.
  2017-05-12
  - version: 0.06b
    added: Joystick support.
    improvement: Unified object drawing.
  2017-05-11
  - version: 0.05b
    added: Mouse support.
  2017-05-10
  - version: 0.04b
    added: Automatically build object from JSON definition.
    added: Keyboard support.
  2017-05-08
  - version: 0.03b
    improvement: Check for TrueType fonts on start up.
    improvement: Removed __presentation() method.
  2017-04-04
  - version: 0.02b
    added: Image class to manage images easily.
  2017-04-01
  - version: 0.01b
    added: version information.
  2016-05-12
  - version: 0.00b
    added: Scrach version.
"""

import os
import os.path
import subprocess
import re
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *  # pylint: disable=wildcard-import, unused-import, unused-wildcard-import
from tools.device import DeviceProperties
from tools.host import HostProperties
import tools.echo as echo
from tools.button import Button
from tools.image import Image
from tools.screensaver import Screensaver
from tools.session import Session
from tools.pytimer.pytimer import Timer
import tools.joystick.joystick as joystick


class Gui:  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """
    description:
    """

    def __init__(self, data):  # pylint: disable=too-many-statements
        self._version = 0.20
        self.__work_dir = os.path.dirname(os.path.realpath(__file__))
        self.__work_dir = os.path.join(self.__work_dir, '../')
        self.__img_dir = os.path.join(self.__work_dir, 'images')
        self.screen_full = False
        self.screen_size = "480x320"
        self.screen_rate = 30
        self.screensaver_time = 60
        self.screensaver_type = 'black'
        self.screensaver_enable = False
        self.screen = None
        self.screen_resolution = None
        self.screensaver = None
        self.screensaver_timer = None
        self.controls = None
        self.object_area = None
        self.status_bar = None
        self.clock = None
        self.background = None
        self.host = None
        self.session = None
        self.running = None
        self.device = None
        self.device_timer = Timer(1000)
        self.connected_devices = None
        self.was_connected = None
        self.joystick = None
        self.joystick_detected = set()
        self.joystick_timer = Timer(1000)
        self.joyicon = None
        self.ctrl_joystick_delay = None
        self.control_joystick_button = None
        self.control_joystick_delay = None
        self.control_joystick_enable = None
        self.control_joystick_speed = None
        self.keyboard = None
        self.control_keyboard_button = None
        self.control_keyboard_delay = None
        self.control_keyboard_speed = None
        self.mouse = None
        self.ctrl_mouse_delay = None
        self.control_mouse_button = None
        self.control_mouse_delay = None
        self.control_mouse_speed = None
        self.touch = None
        self.control_touch_button = None
        self.ctrl_touch_delay = None
        self.control_touch_delay = None
        self.control_touch_enable = None
        self.control_touch_speed = None
        self.control_touch_visible = None
        self.window_caption = None
        self.window_title = None
        self.load(data)
        self.reset()

    def reset(self):
        """
        description:
        """
        self.device = DeviceProperties(self.data)
        self.window_title = 'xC'
        self.window_caption = 'xC - Axes Controller'
        self.was_connected = False
        self.connected_devices = 0

    def load(self, data):
        """
        description:
        """
        self.data = data

    def ctrl_joystick_stop(self):
        """
        description:
        """
        self.joystick.disable()

    def ctrl_joystick_handle(self, event):  # pylint: disable=too-many-branches
        """
        description:
        """
        if not self.control_joystick_enable:
            return
        # Buttons
        for i in self.device.get_objects():
            try:
                if i["control"]["joystick"].split("[")[0] != "button":
                    continue
            except BaseException:
                continue
            i["source"] = ''
            button = int(re.findall('\\b\\d+\\b', i["control"]["joystick"])[0])
            if event.type == JOYBUTTONDOWN and \
               self.joystick.button()[button]:
                i["source"] = 'joystick'
                if i["type"] == "switch":
                    i["button"].toggle()
                elif i["type"] == "push-button":
                    i["button"].on()
            else:
                if event.type == JOYBUTTONUP and \
                   i["type"] == "push-button":
                    i["button"].off()
        # Digital motion (hat)
        # if (event.type == JOYHATMOTION or self.joystick_hat_active):
            # for i in self.device.get_objects():
                # try:
                    # i["control"]["joystick"]
                # except BaseException:
                    # continue
                # if i["control"]["joystick"].split("[")[0] == "hat":
                    # hat = []
                    # for j in range(self.joystick.get_numhats()):
                        # hat.append(self.joystick.get_hat(j))
                        # infoln("hat[" + str(j) + "] = " + str(hat[j]))
                    # if 1 in hat[0] or -1 in hat[0]:
                        # self.joystick_hat_active = True
                    # else:
                        # self.joystick_hat_active = False
                    # if eval(i["control"]["joystick"]):
                        # i["button"].on()
                    # else:
                        # i["button"].off()
        # Analog motion
        if event.type == JOYAXISMOTION:  # pylint: disable=undefined-variable
            for i in self.device.get_objects():
                try:
                    i["control"]["joystick"]
                except BaseException:
                    continue
                if i["control"]["joystick"].split("[")[0] == "axis":
                    axis = re.findall(
                        '\\b\\d+\\b',
                        i["control"]["joystick"])
                    axis = int(axis[0])
                    signal = 0
                    if i["control"]["joystick"][-1:] == "+":
                        signal = 1
                    elif i["control"]["joystick"][-1:] == "-":
                        signal = -1
                    value = self.joystick.axis()[axis]
                    if value * signal * 1000 > 1:
                        i["button"].on()
                        factor = abs(value * self.control_joystick_speed)
                        i["factor"] = str(factor)
                    else:
                        i["button"].off()
                        i["factor"] = '1'

    def ctrl_joystick_start(self, quiet=False):
        """
        description:
        """
        if not quiet:
            echo.info('Joystick: ', 1)
        # Is enable?
        try:
            self.control_joystick_enable = (
                self.device.get_control()["joystick"]["enable"])
        except BaseException:
            self.control_joystick_enable = False
        # Speed
        try:
            self.control_joystick_speed = (
                self.device.get_control()["joystick"]["speed"])
        except BaseException:
            self.control_joystick_speed = 1
        # Delay
        try:
            self.control_joystick_delay = (
                self.device.get_control()["joystick"]["delay"])
        except BaseException:
            self.control_joystick_delay = 50
        # Draw
        self.joyicon = Image(
            self.controls,
            os.path.join(self.__img_dir, 'joystick.png'), [2, 1])
        self.control_joystick_button = Button(
            self.joyicon, [0, 100], [5, 58], self.control_joystick_enable)
        # Detect and start
        self.joystick = joystick.Joystick()
        if joystick.detect():
            if quiet:
                echo.info('Joystick: ', 1)
            self.joystick.identification(joystick.detect()[0])
            echo.infoln(self.joystick.configuration()['name'])
            self.ctrl_joystick_delay = Timer(self.control_joystick_delay)
            echo.debug('Enable: ', 2)
            echo.debugln(str(self.control_joystick_enable))
            echo.debugln('Axes: ' +
                         str(self.joystick.configuration()['axes']), 2)
            echo.debugln('Buttons: ' +
                         str(self.joystick.configuration()['buttons']), 2)
            echo.debugln('Balls: ' +
                         str(self.joystick.configuration()['balls']), 2)
            echo.debugln('Hats: ' +
                         str(self.joystick.configuration()['hats']), 2)
            echo.debugln('Speed: ' +
                         str(self.control_joystick_speed) + '%', 2)
            echo.debugln('Delay: ' +
                         str(self.control_joystick_delay) + 'ms', 2)
        else:
            self.control_joystick_enable = False
            if not quiet:
                echo.infoln('None')

    def ctrl_keyboard_stop(self):  # pylint: disable=no-self-use
        """
        description:
        """
        return False

    def ctrl_keyboard_handle(self, event):  # pylint: disable=too-many-branches
        """
        description:
        """
        # Program behavior
        if event.type == KEYDOWN:  # pylint: disable=undefined-variable
            # Escape
            if event.key == K_ESCAPE:  # pylint: disable=undefined-variable
                self.running = False
            # Keyboard grab
            if event.key == K_F8:  # pylint: disable=undefined-variable
                self.control_keyboard_button.toggle()
            # Mouse grab
            if event.key == K_F9:  # pylint: disable=undefined-variable
                self.control_mouse_button.toggle()
            # Joystick grab
            if event.key == K_F10:  # pylint: disable=undefined-variable
                self.control_joystick_button.toggle()
            # Touch grab
            if event.key == K_F11:  # pylint: disable=undefined-variable
                self.control_touch_button.toggle()
            # Release controls
            if event.key == K_LALT:  # pylint: disable=undefined-variable
                self.control_keyboard_button.off()
                self.control_mouse_button.off()
                self.control_joystick_button.off()
                self.control_touch_button.off()
        # Object behavior
        if not self.control_keyboard_button.get_state():
            return
        for i in self.device.get_objects():
            try:
                i["control"]["keyboard"]
            except BaseException:
                continue
            if i["type"] == "push-button":
                if event.type == KEYDOWN and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["button"].on()
                if event.type == KEYUP and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["button"].off()
            elif i["type"] == "switch":
                if event.type == KEYDOWN and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["button"].toggle()

    def ctrl_keyboard_start(self):
        """
        description:
        """
        echo.info('Keyboard: ', 1)
        # Is enable?
        try:
            control_keyboard_enable = (self.device.get_control()
                                       ["keyboard"]["enable"])
        except BaseException:
            control_keyboard_enable = False
        # Is speed configured?
        try:
            self.control_keyboard_speed = (self.device.get_control()
                                           ["keyboard"]["speed"])
        except BaseException:
            self.control_keyboard_speed = 1
        # Is delay configured?
        try:
            self.control_keyboard_delay = (self.device.get_control()
                                           ["keyboard"]["delay"])
        except BaseException:
            self.control_keyboard_delay = 1
        # Draw
        self.keyboard = Image(self.controls,
                              os.path.join(self.__img_dir, 'keyboard.png'),
                              [2, 1])
        self.control_keyboard_button = Button(self.keyboard, [0, 0], [5, 58],
                                              control_keyboard_enable)
        # Check for device
        check_input = os.path.join(self.__work_dir, 'scripts/check_input.sh')
        cmd = [check_input, 'keyboard']
        # null = open(os.devnull, 'w')
        return_code = subprocess.call(cmd)
        if return_code == 0:
            echo.infoln('Found')
            echo.debug('Enable: ', 2)
            echo.debugln(str(self.control_keyboard_button.get_state()))
            echo.debugln('Speed: ' + str(self.control_keyboard_speed) + 'ms', 2)
            echo.debugln('Delay: ' + str(self.control_keyboard_delay) + 'ms', 2)
        else:
            echo.infoln('None')
        pygame.key.set_repeat(1, 100)

    def ctrl_mouse_stop(self):  # pylint: disable=no-self-use
        """
        description:
        """
        pygame.event.set_grab(False)

    def ctrl_mouse_cursor(self, state):  # pylint: disable=no-self-use
        """
        description:
        """
        off = ("        ",  # sized 8x8
               "        ",
               "        ",
               "        ",
               "        ",
               "        ",
               "        ",
               "        ")
        curs, mask = pygame.cursors.compile(off, ".", "X")
        cursor = ((8, 8), (5, 1), curs, mask)
        if state:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
        else:
            pygame.mouse.set_cursor(*cursor)

    def ctrl_mouse_handle(self, event):
        """
        description:
        """
        if not self.control_mouse_button.get_state():
            return
        if event.type == MOUSEMOTION:  # pylint: disable=undefined-variable
            relative = pygame.mouse.get_rel()
            x = relative[0]  # pylint: disable=invalid-name,unused-variable
            y = relative[1]  # pylint: disable=invalid-name,unused-variable
            for i in self.device.get_objects():
                try:
                    i["control"]["mouse"]
                except BaseException:
                    continue
                if eval(i["control"]["mouse"]):
                    # i["state"] = i["on"]["picture"]
                    if self.session.is_connected():
                        try:
                            peuda = eval(i["control"]["mouse"].split(" ")[0])
                            peuda = abs(peuda * self.control_mouse_speed)
                            peuda = int(round(peuda))
                            i["factor"] = str(peuda)
                            i["button"].on()
                            if int(peuda) == 0:
                                continue
                        except BaseException:
                            pass
                else:
                    i["button"].off()

    def ctrl_mouse_start(self):
        """
        description:
        """
        echo.info('Mouse: ', 1)
        # Is enable?
        try:
            control_mouse_enable = (self.device.get_control()
                                    ["mouse"]["enable"])
        except BaseException:
            control_mouse_enable = False
        # Is speed configured?
        try:
            self.control_mouse_speed = (self.device.get_control()
                                        ["mouse"]["speed"])
        except BaseException:
            self.control_mouse_speed = 100
        try:
            self.control_mouse_delay = (self.device.get_control()
                                        ["mouse"]["delay"])
        except BaseException:
            self.control_mouse_delay = 100
        # Draw
        self.mouse = Image(self.controls,
                           os.path.join(self.__img_dir, 'mouse.png'),
                           [2, 1])
        self.control_mouse_button = Button(self.mouse, [0, 50], [5, 58],
                                           control_mouse_enable)
        # Check for device
        check_input = os.path.join(self.__work_dir, 'scripts/check_input.sh')
        cmd = [check_input, 'mouse']
        # null = open(os.devnull, 'w')
        return_code = subprocess.call(cmd)
        if return_code == 0:
            self.ctrl_mouse_delay = Timer(self.control_mouse_delay)
            echo.infoln('Found')
            echo.debug('Enable: ', 2)
            echo.debugln(str(self.control_mouse_button.get_state()))
            echo.debugln('Speed: ' + str(self.control_mouse_speed) + '%', 2)
        else:
            echo.infoln('None')

    def ctrl_touch_stop(self):  # pylint: disable=no-self-use
        """
        description:
        """
        return False

    def ctrl_touch_handle(self, event):
        """
        description:
        """
        # Program behavior
        if event.type == MOUSEBUTTONUP:  # pylint: disable=undefined-variable
            self.control_keyboard_button.check(pygame.mouse.get_pos())
            self.control_mouse_button.check(pygame.mouse.get_pos())
            self.control_joystick_button.check(pygame.mouse.get_pos())
            self.control_touch_button.check(pygame.mouse.get_pos())
        # Object behavior
        if not self.control_touch_button.get_state():
            return
        for i in self.device.get_objects():
            if i["type"] == 'push-button':
                if event.type == MOUSEBUTTONDOWN:  # pylint: disable=undefined-variable
                    i["button"].check(pygame.mouse.get_pos())
                if event.type == MOUSEBUTTONUP:  # pylint: disable=undefined-variable
                    i["button"].off()
            elif i["type"] == 'switch':
                if event.type == MOUSEBUTTONUP:  # pylint: disable=undefined-variable
                    i["button"].check(pygame.mouse.get_pos())

    def ctrl_touch_start(self):
        """
        description:
        """
        echo.info('Touch: ', 1)
        try:
            self.control_touch_enable = (self.device.get_control()
                                         ["touch"]["enable"])
        except BaseException:
            self.control_touch_enable = False
        # Speed
        try:
            self.control_touch_speed = (self.device.get_control()
                                        ["touch"]["speed"])
        except BaseException:
            self.control_touch_speed = False
        # Visible
        try:
            self.control_touch_visible = (self.host.get_control()
                                          ["touch"]["visible"])
        except BaseException:
            self.control_touch_visible = 1
        # Delay
        try:
            self.control_touch_delay = (self.device.get_control()
                                        ["touch"]["delay"])
        except BaseException:
            self.control_touch_delay = 1
        self.ctrl_touch_delay = Timer(self.control_touch_delay)
        echo.infoln('Found')
        echo.debug('Enable: ', 2)
        echo.debugln(str(self.control_touch_enable))
        self.touch = Image(self.controls,
                           os.path.join(self.__img_dir, 'touch.png'),
                           [2, 1])
        self.control_touch_button = Button(self.touch, [0, 150], [5, 58],
                                           self.control_touch_enable)

    def start_session(self):
        """
        description:
        """
        self.session = Session(self.device.get_comm())
        self.session.info()
        self.session.start()
        if self.session.is_connected_serial():
            while not self.session.is_ready():
                continue
            # self.session.clear()
            for command in self.device.get_startup()["command"]:
                self.session.send_wait(command)
            self.was_connected = True

    def draw_device(self):
        """
        description:
        """
        # Device name
        font = pygame.font.SysFont('Ubuntu', 22)
        text = font.render(self.window_caption, True, (100, 100, 100))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        textpos[1] += 10
        self.screen.blit(text, textpos)

    def stop_session(self):
        """
        description:
        """
        if not self.session.is_connected_serial():
            return
        echo.infoln('Session...')
        while not self.session.is_ready():
            continue
        echo.infoln('Terminating...', 1)
        for command in self.device.get_endup()["command"]:
            self.session.send_wait(command)
        self.session.stop()
        self.was_connected = False

    def stop_ctrl(self):
        """
        description:
        """
        self.ctrl_joystick_stop()
        self.ctrl_keyboard_stop()
        self.ctrl_mouse_stop()
        self.ctrl_touch_stop()

    def stop(self):
        """
        description:
        """
        self.stop_ctrl()
        self.stop_session()
        self.host.stop()
        pygame.quit()  # pylint: disable=no-member

    def draw_object(self):
        """
        description:
        """
        self.object_area.fill([0, 0, 0])  # Black
        for i in self.device.get_objects():
            i["button"].draw()
        self.screen.blit(self.object_area, [65, 50])

    def run(self):
        """
        description:
        """
        echo.infoln('Ready...')
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # pylint: disable=no-member
                    self.running = False
                self.ctrl_check(event)
            if self.joystick_timer.check() and \
               self.joystick.identification() is None:
                self.ctrl_joystick_start(quiet=True)
            self.draw()
            self.ctrl_handle()
            self.device_check()
        echo.infoln("Exiting...")
        self.stop()
        return False

    def ctrl_handle(self):
        """
        description:
        """
        # Mouse visible
        if self.control_mouse_button.get_state() or \
            (self.control_touch_button.get_state() and not
             self.control_touch_visible):
            self.ctrl_mouse_cursor(False)
        else:
            self.ctrl_mouse_cursor(True)
        # Mouse grab
        if self.control_mouse_button.get_state():
            pygame.event.set_grab(True)
        else:
            pygame.event.set_grab(False)
        # Objects
        for i in self.device.get_objects():
            if (i["source"] == 'joystick') and \
               (not self.ctrl_joystick_delay.check()):
                continue
            # Push button (pulse)
            if i["type"] == 'push-button' and \
               i["button"].get_state() and \
               i["timer"].check() and \
               self.session.is_connected():
                command = i["on"]["command"].replace('*', i["factor"])
                self.session.send_wait(command)
            # Switch
            elif i["type"] == 'switch' and \
                 i["button"].get_change() and \
                 self.session.is_connected():
                i["state"] = "on" if i["button"].get_state() else "off"
                command = i[i["state"]]["command"]
                self.session.send_wait(command)

    def ctrl_check(self, event):
        """
        description:
        """
        self.screensaver_timer.reset()
        if self.screensaver.running:
            self.screensaver.stop()
            return
        self.ctrl_keyboard_handle(event)
        self.ctrl_mouse_handle(event)
        self.ctrl_joystick_handle(event)
        self.ctrl_touch_handle(event)
        self.ctrl_handle()

    def draw_ctrl(self):
        """
        description:
        """
        self.controls.fill([0, 0, 0])  # Black
        self.control_keyboard_button.draw()
        self.control_mouse_button.draw()
        self.control_joystick_button.draw()
        self.control_touch_button.draw()
        self.screen.blit(self.controls, (5, 58))

    def draw_screensaver(self):
        """
        description:
        """
        if self.screensaver_timer.check() and not self.screensaver.running:
            self.screensaver.style(self.screensaver_type)
            self.screensaver.start()
        if self.screensaver.running:
            self.screensaver.run()

    def draw(self):
        """
        description:
        """
        self.screen.blit(self.background, (0, 0))
        self.draw_ctrl()
        self.draw_object()
        self.draw_device()
        self.draw_status()
        self.draw_screensaver()
        self.clock.tick(self.screen_rate)
        pygame.display.flip()

    def start_host(self):
        """
        description:
        """
        self.host = HostProperties(self.data["host"])
        self.host.info()
        echo.debugln("pygame: " + pygame.version.ver, 1)
        self.host.start()
        # Get Screen parameters
        try:
            self.screen_full = self.host.get_screen()["full"]
            self.screen_size = self.host.get_screen()["size"]
            self.screen_rate = self.host.get_screen()["rate"]
        except BaseException:
            pass
        # Get Screensaver parameters
        try:
            self.screensaver_time = self.host.get_screensaver() \
                .get('time', self.screensaver_time)
            if self.screensaver_time < 1:
                self.screensaver_time = 1
            self.screensaver_type = self.host.get_screensaver() \
                .get('type', self.screensaver_type)
            self.screensaver_enable = self.host.get_screensaver() \
                .get('enable', self.screensaver_enable)
        except BaseException:
            pass

    def start_objects(self):
        """
        description:
        """
        for i in self.device.get_objects():
            i["image"] = Image(self.object_area,
                               os.path.join(self.__img_dir,
                                            i["picture"]["file"]),
                               eval(i["picture"]["split"]))
            i["boolean"] = i["default"] == "on"
            # infoln('ID: ' + str(i["id"]) + ", default: " + str(i["default"]))
            i["source"] = ''
            i["factor"] = '1'
            i["button"] = Button(i["image"],
                                 eval(i["picture"]["position"]),
                                 [65, 50],
                                 i["boolean"])
            try:
                i["timer"] = Timer(i["delay"])
            except BaseException:
                i["timer"] = Timer(20)
            i["state"] = i["default"]
        if len(self.device.get_objects()):
            echo.infoln('Objects...')
            echo.infoln('Imported: ' + str(len(self.device.get_objects())), 1)

    def device_set(self, device_id):
        """
        description:
        """
        self.device.set(device_id)

    def device_check(self):
        """
        description:
        """
        if not self.device_timer.check():
            return False
        # Reset all data if device was unpluged.
        if not self.session.is_connected_serial() and self.was_connected:
            self.reset()
            self.device.reset()
            self.start_device()
            self.ctrl_start()
            self.start_objects()
            self.session.reset()
            self.start_session()
        if self.device.get_id() is None:
            # How many devices are connected?
            devices = self.device.detect()
            # If is just one...
            if len(devices) == 1:
                # Configure a new device.
                self.session.reset()
                self.start_device()
                self.ctrl_start()
                self.start_objects()
                self.start_session()
                return False
            # Abort if are more than one.
            if len(devices) > 1 and (len(devices) != self.connected_devices):
                self.connected_devices = len(devices)
                echo.infoln('Too many connected devices: ' + str(devices), 1)
        return False

    def start_device(self):
        """
        description:
        """
        echo.infoln("Device...")
        if not self.device.get_id():
            detected = self.device.detect()
            if len(detected) > 1:
                echo.warnln('Too many connected devices: ' + str(detected), 1)
                return
        self.device.info()
        if self.device.get_id():
            self.window_title = self.device.system_plat + ' Mark ' + \
                self.device.system_mark
            self.window_caption = self.device.system_plat + ' Mark ' + \
                self.device.system_mark + ' - ' + \
                self.device.system_desc

    def start_screen(self):
        """
        description:
        """
        # global pygame
        echo.infoln("Screen...")
        # Set screen resolution
        self.screen_resolution = [int(s) for s in self.screen_size.split('x')
                                  if s.isdigit()]
        # Check for minimum resolution
        if (self.screen_resolution[0] < 480) or \
           (self.screen_resolution[1] < 320):
            self.screen_resolution = (480, 320)
        self.screen_resolution[0] -= 1
        self.screen_resolution[1] -= 1
        echo.infoln("Size: " + str(self.screen_resolution[0] + 1) + 'x' +
                    str(self.screen_resolution[1] + 1) + ' px', 1)
        echo.infoln("Refresh rate: " + str(self.screen_rate) + ' FPS', 1)
        # Positioning
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        # Initialise screen
        pygame.init()  # pylint: disable=no-member
        self.screen = pygame.display.set_mode(self.screen_resolution)
        if self.screen_full:
            pygame.display.toggle_fullscreen()
        # Window caption
        pygame.display.set_caption(self.window_title)
        # Checking fonts
        echo.debugln('Checking fonts...', 1)
        for ttf_name in ['Digital Readout Thick Upright',
                         'Ubuntu']:
            ttf_path = pygame.font.match_font(ttf_name)
            if ttf_path is None:
                echo.erroln('TrueType font missing.')
                echo.infoln('\"' + str(ttf_name) + '\" not found (' +
                            str(ttf_path) + ')', 2)
        # Background
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill([0, 0, 0])  # Black
        # Controls area
        self.controls = pygame.Surface([120, 240])
        # Object area
        self.object_area = pygame.Surface([self.screen.get_size()[0] - 65,
                                           self.screen.get_size()[1] - 70])
        # Status bar
        self.status_bar = pygame.Surface([self.screen.get_size()[0], 16])
        # Clockling
        echo.debugln('Clockling...', 1)
        self.clock = pygame.time.Clock()
        # Screensaver
        self.screensaver = Screensaver(self.screen)
        self.screensaver_timer = Timer(1000 * self.screensaver_time, 'COUNTDOWN')
        if not self.screensaver_enable:
            self.screensaver_timer.disable()

    def ctrl_start(self):
        """
        description:
        """
        echo.infoln('Input...')
        self.ctrl_keyboard_start()
        self.ctrl_mouse_start()
        self.ctrl_joystick_start()
        self.ctrl_touch_start()

    def start(self):
        """
        description:
        """
        self.start_host()
        self.start_screen()
        self.start_device()
        self.ctrl_start()
        self.start_objects()
        self.start_session()

    def draw_status(self):
        """
        description:
        """
        # Status bar
        pygame.draw.rect(self.status_bar, (0, 29, 0),
                         (0, 0, self.status_bar.get_size()[0],
                          self.status_bar.get_size()[1]))
        font = pygame.font.SysFont("Digital Readout Thick Upright", 13)
        # Frame rate
        fps = str("FPS: {:1.1f}".format(float(self.clock.get_fps())))
        text = font.render(fps, True, (32, 128, 32))
        textpos = text.get_rect()
        textpos.bottomleft = self.status_bar.get_rect().bottomleft
        textpos[0] += 3
        self.status_bar.blit(text, textpos)
        # Device connection status
        connection = 'Connected' if self.session.is_connected() \
                     else 'Disconnected'
        text = font.render(connection, True, (32, 128, 32))
        textpos = text.get_rect()
        textpos.bottomright = self.status_bar.get_rect().bottomright
        textpos[0] += -3
        self.status_bar.blit(text, textpos)
        # General information
        text = font.render(str(self.host.status()), True, (32, 128, 32))
        textpos = text.get_rect()
        textpos.midbottom = self.status_bar.get_rect().midbottom
        self.status_bar.blit(text, textpos)
        self.screen.blit(self.status_bar, [0, self.screen.get_size()[1] - 16])
