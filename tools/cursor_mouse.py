"""
---
name: cursor_mouse.py
description: Cursor Mouse
copyright: 2016-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  contributors:
  - name: None
change-log:
  2019-12-15
  - version: 0.1
    added: Scrach version.
"""

import contextlib
with contextlib.redirect_stdout(None):
    import pygame

__version__ = 0.1

def cursor_mouse(status):
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
    if status is True:
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
    elif status is False:
        pygame.mouse.set_cursor(*cursor)
    return status
