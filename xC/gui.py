"""
gui.py

Author: Marcio Pessoa <marcio.pessoa@sciemon.com>
Contributors: none

Change log:
2018-06-27
        * Version: 0.17b
        * Changed: Removed resizeable window feature.

2018-06-19
        * Version: 0.16b
        * Added: Pong easter egg

2018-06-05
        * Version: 0.15b
        * Added: CPU Core number.

2018-01-27
        * Version: 0.14b
        * Added: Screen resolution customization.

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
        * Added: Image class to manage images easily.

2017-04-01
        * Version: 0.01b
        * Added: Version information.

2016-05-12
        * Version: 0.00b
        * Scrach version.
"""

import sys
import os.path
import os
import pygame
from pygame.locals import *
import subprocess
import time
from xC.device import DeviceProperties
from xC.host import HostProperties
from xC.echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln
from xC.session import Session
from xC.timer import Timer
from xC.pong import Pong

xc_path = os.getenv('XC_PATH', '/opt/sciemon/xc')
images_directory = os.path.join(xc_path, 'images')


class Gui:
    """  """

    def __init__(self, data):
        self.version = '0.17b'
        self.window_title = 'xC'
        self.window_caption = 'xC - Axes Controller'
        self.load(data)
        self.screen_full = False
        self.screen_size = "480x320"
        self.screen_rate = 30
        self.device_id = None

    def load(self, data):
        self.data = data

    def ctrl_joystick_stop(self):
        pygame.joystick.quit()

    def ctrl_joystick_handle(self, event):
        if self.control_joystick_enable is not True:
            return
        if (event.type == JOYBUTTONDOWN or event.type == JOYBUTTONUP):
            for i in self.device.get_objects():
                try:
                    i["control"]["joystick"]
                except BaseException:
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
                            if self.session.is_connected():
                                self.session.send_wait(command)
                        if i["type"] == "switch":
                            state = True if i["state"] == "on" else False
                            state = not state
                            i["state"] = "on" if state else "off"
                            # infoln("b[" + str(j) + "] state = " + i["state"])
                            command = i[i["state"]]["command"]
                            if self.session.is_connected():
                                self.session.send_wait(command)
        if (event.type == JOYHATMOTION or self.joystick_hat_active):
            for i in self.device.get_objects():
                try:
                    i["control"]["joystick"]
                except BaseException:
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
                        if self.session.is_connected():
                            n = 1
                            command = i["on"]["command"].replace('*', str(n))
                            self.session.send_wait(command)
                    else:
                        i["state"] = i["off"]["picture"]
        if event.type == JOYAXISMOTION:
            if self.joystick_timer.check() is not True:
                return
            # Search for configured axes
            for i in self.device.get_objects():
                try:
                    i["control"]["joystick"]
                except BaseException:
                    continue
                if event.type == pygame.JOYAXISMOTION and \
                   i["control"]["joystick"].split("[")[0] == "axis":
                    axis = []
                    for j in range(self.joystick.get_numaxes()):
                        axis.append(self.joystick.get_axis(j))
                        # infoln("axis[" + str(j) + "] = " + str(axis[j]))
                    if eval(i["control"]["joystick"]):
                        i["state"] = i["on"]["picture"]
                        if self.session.is_connected():
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
        info('Joystick: ', 1)
        # Is enable?
        try:
            self.control_joystick_enable = (self.device.get_control()
                                            ["joystick"]["enable"])
        except BaseException:
            self.control_joystick_enable = False
        # Is speed configured?
        try:
            self.control_joystick_speed = (self.device.get_control()
                                           ["joystick"]["speed"])
        except BaseException:
            self.control_joystick_speed = 1
        # Draw
        self.joyicon = Image(self.controls,
                             os.path.join(images_directory, 'joystick.png'),
                             [2, 1])
        self.control_joystick_button = Button(self.joyicon, [0, 100], [5, 58],
                                              self.control_joystick_enable)
        self.joystick_hat_active = False
        # Detect and start
        joysticks = pygame.joystick.get_count()
        if joysticks:
            infoln(str(joysticks))
            for i in range(joysticks):
                self.joystick = pygame.joystick.Joystick(i)
                self.joystick.init()
                try:
                    delay = self.device.get_control()["joystick"]["delay"]
                except BaseException:
                    delay = 100
                self.joystick_timer = Timer(delay)
                info('Enable: ', 2)
                infoln(str(self.control_joystick_enable))
                infoln(self.joystick.get_name(), 2)
                infoln('Axes: ' + str(self.joystick.get_numaxes()), 3)
                infoln('Buttons: ' + str(self.joystick.get_numbuttons()), 3)
                infoln('Balls: ' + str(self.joystick.get_numballs()), 3)
                infoln('Hats: ' + str(self.joystick.get_numhats()), 3)
                infoln('Speed: ' + str(self.control_joystick_speed) + '%', 3)
                infoln('Delay: ' + str(delay) + 'ms', 3)
        else:
            infoln('None')

    def ctrl_keyboard_stop(self):
        pass

    def ctrl_keyboard_handle(self, event):
        # Program behavior
        if self.pong.running:
            self.pong.control(event)
            return False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:  # Escape
                self.running = False
            if event.key == K_F1:  # Help screen
                help_screen_on = True
            if event.key == K_F8:  # Keyboard grab
                self.control_keyboard_button.toggle()
            if event.key == K_F9:  # Mouse grab
                self.control_mouse_button.toggle()
            if event.key == K_F10:  # Joystick grab
                self.control_joystick_button.toggle()
            if event.key == K_F11:  # Touch grab
                self.control_touch_button.toggle()
            if event.key == K_F12:  # Voice grab
                self.control_voice_button.toggle()
            if event.key == K_p:  # Pong
                self.pong.start()
            if event.key == K_LALT:  # Release controls
                self.control_keyboard_button.off()
                self.control_mouse_button.off()
                self.control_joystick_button.off()
                self.control_touch_button.off()
                self.control_voice_button.off()
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
                    i["state"] = i["on"]["picture"]
                    i["button"].on()
                    if self.session.is_connected():
                        command = i["on"]["command"] .replace('*', '1')
                        self.session.send_wait(command)
                if event.type == KEYUP and \
                   event.key == eval(i["control"]["keyboard"]):
                    i["button"].off()
                    i["state"] = i["off"]["picture"]
            elif i["type"] == "switch":
                if event.type == KEYDOWN and \
                   event.key == eval(i["control"]["keyboard"]):
                    state = True if i["state"] == "on" else False
                    state = not state
                    i["button"].toggle()
                    i["state"] = "on" if state else "off"
                    if self.session.is_connected():
                        command = i[i["state"]]["command"].replace('*', '1')
                        self.session.send_wait(command)
                if event.type == KEYUP and \
                   event.key == eval(i["control"]["keyboard"]):
                    pass

    def ctrl_keyboard_start(self):
        info('Keyboard: ', 1)
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
                              os.path.join(images_directory, 'keyboard.png'),
                              [2, 1])
        self.control_keyboard_button = Button(self.keyboard, [0, 0], [5, 58],
                                              control_keyboard_enable)
        # Check for device
        check_input = os.path.join(xc_path, 'scripts/check_input.sh')
        cmd = [check_input, 'keyboard']
        null = open(os.devnull, 'w')
        return_code = subprocess.call(cmd)
        if return_code == 0:
            infoln('Found')
            info('Enable: ', 2)
            infoln(str(self.control_keyboard_button.get_state()))
            infoln('Speed: ' + str(self.control_keyboard_speed) +
                   'ms', 2)
            infoln('Delay: ' + str(self.control_keyboard_delay) +
                   'ms', 2)
        else:
            infoln('None')
        pygame.key.set_repeat(1, 100)

    def ctrl_mouse_stop(self):
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def ctrl_mouse_cursor(self, state):
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
        if not self.control_mouse_button.get_state():
            return
        if event.type == MOUSEMOTION:
            r = pygame.mouse.get_rel()
            x = r[0]
            y = r[1]
            if x == 0 and y == 0:
                return
            #
            for i in self.device.get_objects():
                try:
                    i["control"]["mouse"]
                except BaseException:
                    continue
                if eval(i["control"]["mouse"]):
                    i["state"] = i["on"]["picture"]
                    if self.session.is_connected():
                        try:
                            n = eval(i["control"]["mouse"].split(" ")[0])
                            n = abs(n * self.control_mouse_speed)
                            n = int(round(n))
                            if int(n) == 0:
                                continue
                            command = i["on"]["command"].replace('*', str(n))
                            self.session.send_wait(command)
                        except BaseException:
                            pass
                else:
                    i["state"] = i["off"]["picture"]

    def ctrl_mouse_start(self):
        info('Mouse: ', 1)
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
        # Draw
        self.mouse = Image(self.controls,
                           os.path.join(images_directory, 'mouse.png'),
                           [2, 1])
        self.control_mouse_button = Button(self.mouse, [0, 50], [5, 58],
                                           control_mouse_enable)
        # Check for device
        check_input = os.path.join(xc_path, 'scripts/check_input.sh')
        cmd = [check_input, 'mouse']
        null = open(os.devnull, 'w')
        return_code = subprocess.call(cmd)
        if return_code == 0:
            infoln('Found')
            info('Enable: ', 2)
            infoln(str(self.control_mouse_button.get_state()))
            infoln('Speed: ' + str(self.control_mouse_speed) + '%', 2)
        else:
            infoln('None')

    def ctrl_touch_stop(self):
        pygame.mouse.set_visible(True)

    def ctrl_touch_handle(self, event):
        # Program behavior
        if event.type == MOUSEBUTTONUP:
            self.control_keyboard_button.check(pygame.mouse.get_pos())
            self.control_mouse_button.check(pygame.mouse.get_pos())
            self.control_joystick_button.check(pygame.mouse.get_pos())
            self.control_touch_button.check(pygame.mouse.get_pos())
            self.control_voice_button.check(pygame.mouse.get_pos())
        # Object behavior
        if not self.control_touch_button.get_state():
            return
        for i in self.device.get_objects():
            if i["type"] == 'push-button':
                if event.type == MOUSEBUTTONDOWN:
                    i["button"].check(pygame.mouse.get_pos())
                if event.type == MOUSEBUTTONUP:
                    i["button"].off()
            elif i["type"] == 'switch':
                if event.type == MOUSEBUTTONUP:
                    i["button"].check(pygame.mouse.get_pos())
                    if self.session.is_connected() and \
                       i["button"].get_state():
                        if i["button"].get_state():
                            cu = 'off'
                        else:
                            cu = 'on'
                        command = i[cu]["command"].replace('*', '1')
                        self.session.send_wait(command)

    def ctrl_voice_stop(self):
        pass

    def ctrl_touch_start(self):
        info('Touch: ', 1)
        infoln('Not implemented yet.')
        try:
            self.control_touch_enable = (self.device.get_control()
                                         ["touch"]["enable"])
        except BaseException:
            self.control_touch_enable = False
        try:
            self.control_touch_speed = (self.device.get_control()
                                        ["touch"]["speed"])
        except BaseException:
            self.control_touch_speed = 1
        # Delay
        try:
            self.control_touch_delay = (self.device.get_control()
                                        ["touch"]["delay"])
        except BaseException:
            self.control_touch_delay = 1
        self.ctrl_touch_delay = Timer(self.control_touch_delay)
        info('Enable: ', 2)
        infoln(str(self.control_touch_enable))
        self.touch = Image(self.controls,
                           os.path.join(images_directory, 'touch.png'),
                           [2, 1])
        self.control_touch_button = Button(self.touch, [0, 150], [5, 58],
                                           self.control_touch_enable)

    def ctrl_voice_handle(self, event):
        if self.control_voice_enable is False:
            return

    def ctrl_voice_start(self):
        info('Voice: ', 1)
        infoln('Not implemented yet.')
        self.control_voice_enable = False
        info('Enable: ', 2)
        infoln(str(self.control_voice_enable))
        self.voice = Image(self.controls,
                           os.path.join(images_directory, 'voice.png'),
                           [2, 1])
        self.control_voice_button = Button(self.voice, [0, 200], [5, 58],
                                           self.control_voice_enable)

    def start_session(self):
        self.session = Session(self.device.get_comm())
        self.session.info()
        self.session.start()

        if self.session.is_connected():
            while not self.session.is_ready():
                pass
            for c in self.device.get_startup()["command"]:
                self.session.send(c)
                self.session.receive()

    def draw_device(self):
        # Device name
        font = pygame.font.SysFont('Ubuntu', 22)
        text = font.render(self.window_caption, True, (100, 100, 100))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        textpos[1] += 10
        self.screen.blit(text, textpos)

    def stop(self):
        self.ctrl_joystick_stop()
        self.ctrl_keyboard_stop()
        self.ctrl_mouse_stop()
        self.ctrl_touch_stop()
        self.ctrl_voice_stop()
        self.host.stop()
        pygame.quit()

    def images_load(self):
        # Help screen
        self.helpscreen = Image(self.screen,
                                os.path.join(images_directory, 'help.png'))
        imgpos = self.helpscreen.surface.get_rect()
        imgpos.center = self.background.get_rect().center
        self.helpscreen.position(position=imgpos)

    def draw_object(self):
        self.object_area.fill([0, 0, 0])  # Black
        for i in self.device.get_objects():
            i["button"].draw()
        self.screen.blit(self.object_area, [130, 50])

    def run(self):
        infoln('Ready...')
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.ctrl_check(event)
            self.ctrl_handle()
            self.draw()
            self.device_check()
        infoln("Exiting...")
        self.stop()
        return False

    def ctrl_handle(self):
        # Mouse visible
        if self.control_mouse_button.get_state() or \
           self.control_touch_button.get_state():
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
            # Push button (pulse)
            if i["type"] == 'push-button' and \
               i["button"].get_state() and \
               i["timer"].check() and \
               self.session.is_connected():
                    command = i["on"]["command"].replace('*', '1')
                    self.session.send_wait(command)

    def ctrl_check(self, event):
        self.ctrl_keyboard_handle(event)
        self.ctrl_mouse_handle(event)
        self.ctrl_joystick_handle(event)
        self.ctrl_touch_handle(event)
        self.ctrl_voice_handle(event)
        self.ctrl_handle()

    def draw_ctrl(self):
        self.controls.fill([0, 0, 0])  # Black
        self.control_keyboard_button.draw()
        self.control_mouse_button.draw()
        self.control_joystick_button.draw()
        self.control_touch_button.draw()
        self.control_voice_button.draw()
        self.screen.blit(self.controls, (5, 58))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        if self.pong.running:
            self.pong.run()
        else:
            self.draw_ctrl()
            self.draw_object()
            self.draw_device()
        self.draw_status()
        self.clock.tick(self.screen_rate)
        pygame.display.flip()

    def start_host(self):
        self.host = HostProperties(self.data["host"])
        self.host.info()
        self.host.start()
        # Get Screen parameters
        try:
            self.screen_full = self.host.get_screen()["full"]
            self.screen_size = self.host.get_screen()["size"]
            self.screen_rate = self.host.get_screen()["rate"]
        except BaseException:
            pass

    def start_objects(self):
        infoln('Objects...')
        for i in self.device.get_objects():
            i["id"] = Image(self.object_area,
                            os.path.join(images_directory,
                                         i["picture"]["file"]),
                            eval(i["picture"]["split"]))
            i["button"] = Button(i["id"],
                                 eval(i["picture"]["position"]),
                                 [130, 50],
                                 0)
            try:
                i["timer"] = Timer(i["delay"])
            except BaseException:
                i["timer"] = Timer(20)
            i["state"] = i["default"]
        infoln('Imported: ' + str(len(self.device.get_objects())), 1)

    def device_set(self, id):
        self.device_id = id

    def device_load(self, device):
        self.device = device

    def device_check(self):
        pass

    def start_device(self):
        infoln("Device...")
        self.device = DeviceProperties(self.data)
        if not self.device_id:
            self.device_id = self.device.detect()
        if not self.device_id:
            return
        self.device.set(self.device_id)
        self.device.info()
        #
        self.window_title = self.device.system_plat + ' Mark ' + \
            self.device.system_mark
        self.window_caption = self.device.system_plat + ' Mark ' + \
            self.device.system_mark + ' - ' + \
            self.device.system_desc

    def start_screen(self):
        global pygame
        infoln("Screen...")

        # Set screen resolution
        self.screen_resolution = (480, 320)  # pixels (default resolution)
        self.screen_resolution = map(int, self.screen_size.split('x'))
        # Check for minimum resolution
        if (self.screen_resolution[0] < 480) or \
           (self.screen_resolution[1] < 320):
            self.screen_resolution = (480, 320)
        self.screen_resolution[0] -= 1
        self.screen_resolution[1] -= 1

        infoln("Size: " + str(self.screen_resolution[0] + 1) + 'x' +
               str(self.screen_resolution[1] + 1) + ' px', 1)
        infoln("Refresh rate: " + str(self.screen_rate) + ' FPS', 1)

        # Positioning
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        # os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (200, 200)

        # Initialise screen
        pygame.init()

        self.screen = pygame.display.set_mode(self.screen_resolution)

        if self.screen_full:
            pygame.display.toggle_fullscreen()

        # Window caption
        pygame.display.set_caption(self.window_title)

        # Checking fonts
        infoln('Checking fonts...', 1)
        for ttf_name in ['Digital Readout Thick Upright',
                         'Ubuntu']:
            ttf_path = pygame.font.match_font(ttf_name)
            if ttf_path is None:
                erroln('TrueType font missing.')
                infoln('\"' + ttf_name + '\" not found (' + ttf_path + ')', 2)

        # Background
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill([0, 0, 0])  # Black
        # Controls bar
        self.controls = pygame.Surface([120, 240])
        # Object area
        self.object_area = pygame.Surface([self.screen.get_size()[0] - 140,
                                           self.screen.get_size()[1] - 80])
        # Status bar
        self.status_bar = pygame.Surface([self.screen.get_size()[0], 16])

        # Clockling
        infoln('Clockling...', 1)
        self.clock = pygame.time.Clock()

        # Pong
        self.pong = Pong(self.screen)

        # Images
        infoln('Loading images...', 1)
        self.images_load()

    def start_ctrl(self):
        infoln('Input...')
        self.ctrl_keyboard_start()
        self.ctrl_mouse_start()
        self.ctrl_joystick_start()
        self.ctrl_touch_start()
        self.ctrl_voice_start()

    def start(self):
        self.start_host()
        self.start_screen()
        self.start_device()
        self.start_ctrl()
        self.start_objects()
        self.start_session()

    def draw_status(self):
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
        text = font.render(self.host.status(), True, (32, 128, 32))
        textpos = text.get_rect()
        textpos.midbottom = self.status_bar.get_rect().midbottom
        self.status_bar.blit(text, textpos)

        self.screen.blit(self.status_bar, [0, self.screen.get_size()[1] - 16])

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
                |---|---|---|---|
                | 1 | 2 | 3 | 4 |
                |---|---|---|---|
                | 5 | 6 | 7 | 8 |
                |---|---|---|---|

            Take a look at one piece, the piece number 7 for example:
               A|---|B
                | 7 |
               D|---|C

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

    def get_size(self):
        return self.dimensions


class Button:
    def __init__(self, image, position, surface, state=False):
        pass
        self.image = image
        self.size = self.image.get_size()
        self.state = state
        self.position = position
        self.click = [0, 0]
        self.click[0] = position[0] + surface[0]
        self.click[1] = position[1] + surface[1]

    def on(self):
        self.state = True

    def off(self):
        self.state = False

    def draw(self):
        self.image.draw([self.state, 0], self.position)

    def toggle(self):
        self.state = not self.state

    def check(self, mouse):
        if mouse[0] >= self.click[0] and \
           mouse[0] <= self.click[0] + self.size[0] and\
           mouse[1] >= self.click[1] and \
           mouse[1] <= self.click[1] + self.size[1]:
            self.toggle()

    def get_state(self):
        return self.state
