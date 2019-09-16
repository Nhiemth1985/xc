"""
---
name: screensaver.py
description: Screensaver package
copyright: 2018-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
  2019-08-25
  - version: 0.3
    fixed: Some adequations to pylint3.
  2019-01-01
  - version: 0.2
    changed: Python 3 ready.
  2018-07-22
  - version: 0.01
    added: First version.
"""

import random
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *  # pylint: disable=wildcard-import, unused-import, unused-wildcard-import


class Screensaver:
    """
    description:
    """

    def __init__(self, screen):
        self.version = 0.3
        self.__screen = screen
        self.running = False
        self.__style = 'black'
        self.__styles = ['black', 'squares', 'lines', 'circles']
        self.background = pygame.Surface(self.__screen.get_size())  # pylint: disable=too-many-function-args

    def start(self):
        """
        description:
        """
        self.running = True
        self.background.fill([0, 0, 0])  # Black
        pygame.mouse.set_visible(False)

    def style(self, style=None):
        """
        description:
        """
        if style in self.__styles:
            self.__style = style
            return
        if style == 'random':
            self.__style = random.choice(self.__styles)
            return

    def run(self):
        """
        description:
        """
        if self.__style == 'black':
            self.__black()
        elif self.__style == 'squares':
            self.__squares()
        elif self.__style == 'lines':
            self.__lines()
        elif self.__style == 'circles':
            self.__circles()
        self.__screen.blit(self.background, [0, 0])

    def stop(self):
        """
        description:
        """
        self.running = False
        pygame.mouse.set_visible(True)

    def __black(self):
        pass

    def __lines(self):
        colour = [random.randrange(0, 255),
                  random.randrange(0, 255),
                  random.randrange(0, 255)]
        position = [random.randrange(0, self.background.get_size()[0]),
                    random.randrange(0, self.background.get_size()[1])]
        size = [random.randrange(0, self.background.get_size()[0] -
                                 position[0]),
                random.randrange(0, self.background.get_size()[1] -
                                 position[1])]
        pygame.draw.line(self.background, colour,
                         position,
                         size)

    def __squares(self):
        colour = [random.randrange(0, 255),
                  random.randrange(0, 255),
                  random.randrange(0, 255)]
        position = [random.randrange(0, self.background.get_size()[0]),
                    random.randrange(0, self.background.get_size()[1])]
        size = [random.randrange(0, self.background.get_size()[0] -
                                 position[0]),
                random.randrange(0, self.background.get_size()[1] -
                                 position[1])]
        rect = [position[0], position[1], size[0], size[1]]
        pygame.draw.rect(self.background, colour, rect)

    def __circles(self):
        colour = [random.randrange(0, 255),
                  random.randrange(0, 255),
                  random.randrange(0, 255)]
        position = [random.randrange(0, self.background.get_size()[0]),
                    random.randrange(0, self.background.get_size()[1])]
        radius = random.randrange(0, self.background.get_size()[0] / 16)
        pygame.draw.circle(self.background, colour, position, radius)
