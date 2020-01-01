"""
---
name: image.py
description: Image manipulation package
copyright: 2017-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  contributors:
  - name: None
change-log:
  2019-09-07
  - version: 0.2
    added: pylint friendly.
  2017-04-04
  - version: 0.01
    added: Image class to manage images easily.
"""

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *  # pylint: disable=wildcard-import, unused-import, unused-wildcard-import


class Image:  # pylint: disable=too-many-instance-attributes
    """
    description:
    """

    __version__ = 0.2

    def __init__(self, screen, source, splits=None):
        self.source = source
        self.screen = screen
        self.surface = pygame.image.load(self.source)
        self.size = self.surface.get_rect().size
        self.__position = None
        if splits is None:
            splits = [None, None]
        self.splits = splits
        if self.splits != [None, None]:
            self.split(self.splits)

    def draw(self, item=None, position=None):
        """
        description:
        """
        if item is None:
            item = [None, None]
        if position is None:
            position = [None, None]
        if position != [None, None]:
            self.__position = position
        if item == [None, None]:
            self.screen.blit(self.surface, self.__position)
        else:
            if item[0] > (self.splits[0] - 1) or \
               item[1] > (self.splits[1] - 1):
                # echo.warnln('Split image out of range: ' + self.source)
                return True
            self.screen.blit(self.surface, self.__position, self.piece(item))
        return False

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
        corner_a = [0, 0]
        corner_c = [0, 0]
        corner_a[0] = self.dimensions[0] * item[0]
        corner_a[1] = self.dimensions[1] * item[1]
        corner_c[0] = self.dimensions[0]
        corner_c[1] = self.dimensions[1]
        return [corner_a, corner_c]

    def position(self, position):
        """
        description:
        """
        self.__position = position

    def split(self, splits):
        """
        description:
        """
        self.dimensions = [0, 0]
        self.splits = splits
        self.splits_total = self.splits[0] * self.splits[1]
        self.dimensions[0] = self.size[0] / self.splits[0]
        self.dimensions[1] = self.size[1] / self.splits[1]
        return self.splits_total

    def get_size(self):
        """
        description:
        """
        return self.dimensions
