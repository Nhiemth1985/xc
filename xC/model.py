"""
model.py

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log:
2017-05-19
        * Version: 0.00b
        * Scrach version.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
from echo import verbose, level, \
    echo, echoln, erro, erroln, warn, warnln, info, infoln, code, codeln
from timer import Timer

SCREEN_SIZE = (400, 400)  # Pixels
REFRESH_RATE = 60  # Frames per second


class Model:
    """  """

    def __init__(self):
        self.verticies = (
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1))

        self.edges = (
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7))

        pygame.init()
        pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF | OPENGLBLIT)
        gluPerspective(45, (SCREEN_SIZE[0]/SCREEN_SIZE[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)

    def cube(self):
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()

    def draw(self):
        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.cube()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.draw()
            pygame.display.flip()
            pygame.time.wait(60)


def main():
    obj = Model()
    obj.run()


if __name__ == '__main__':
    main()
