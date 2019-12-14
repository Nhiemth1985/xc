"""
---
name: button.py
description: Buttons for GUI
copyright: 2018-2019 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  contributors:
  - name: None
change-log:
  2019-12-14
  - version: 0.3
    fixed: variable names to internal pattern.
    add: state method.
  2019-07-08
  - version: 0.2
    fixed: pylint friendly.
  2018-06-27
  - version: 0.1
    added: My first version.
"""


class Button:
    """
    description:
    """

    def __init__(self, image, position, surface, state=False):
        self._version = 0.3
        self.__image = image
        self.__size = self.__image.get_size()
        self.__state = state
        self.__state_before = self.__state
        self.__position = position
        self.__click = [0, 0]
        self.__click[0] = position[0] + surface[0]
        self.__click[1] = position[1] + surface[1]

    def on(self):  # pylint: disable=invalid-name
        """
        description:
        """
        self.__state = True

    def off(self):
        """
        description:
        """
        self.__state = False

    def draw(self):
        """
        description:
        """
        self.__image.draw([self.__state, 0], self.__position)

    def toggle(self):
        """
        description:
        """
        self.__state = not self.__state

    def check(self, mouse):
        """
        description:
        """
        if mouse[0] >= self.__click[0] and \
           mouse[0] <= self.__click[0] + self.__size[0] and\
           mouse[1] >= self.__click[1] and \
           mouse[1] <= self.__click[1] + self.__size[1]:
            self.toggle()

    def get_state(self):  # TODO: Deprecated (must be removed)
        """
        description:
        """
        return self.__state

    def state(self):
        """
        description:
        """
        return self.__state

    def get_change(self):
        """
        description:
        """
        if self.__state != self.__state_before:
            self.__state_before = self.__state
            return True
        return False
