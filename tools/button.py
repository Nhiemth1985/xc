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
        self._version = 0.2
        self.image = image
        self.size = self.image.get_size()
        self.state = state
        self.state_before = self.state
        self.position = position
        self.click = [0, 0]
        self.click[0] = position[0] + surface[0]
        self.click[1] = position[1] + surface[1]

    def on(self):  # pylint: disable=invalid-name
        """
        description:
        """
        self.state = True

    def off(self):
        """
        description:
        """
        self.state = False

    def draw(self):
        """
        description:
        """
        self.image.draw([self.state, 0], self.position)

    def toggle(self):
        """
        description:
        """
        self.state = not self.state

    def check(self, mouse):
        """
        description:
        """
        if mouse[0] >= self.click[0] and \
           mouse[0] <= self.click[0] + self.size[0] and\
           mouse[1] >= self.click[1] and \
           mouse[1] <= self.click[1] + self.size[1]:
            self.toggle()

    def get_state(self):
        """
        description:
        """
        return self.state

    def get_change(self):
        """
        description:
        """
        if self.state != self.state_before:
            self.state_before = self.state
            return True
        return False
