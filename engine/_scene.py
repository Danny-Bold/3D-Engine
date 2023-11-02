from math import sin, cos, pi

import pygame


class _OffsetHolder:
    def __init__(self, offset):
        """

        Holder offset so that object.offset contains a list/tuple of length 3, for use with composite body rasterizing.

        """
        self.offset = offset


class Scene:
    def __init__(self, *args, screenDim=0, background=(255, 255, 255)):
        self.objs = list(args)
        self.background = background
        self.offset = [0.0, 0.0, 0.0]
        self.rot = [0.0, 0.0]
        self.dim = screenDim
        self.pointMap = lambda point: (self.dim * (1 + point[0]) / 2, self.dim * (1 - point[1]) / 2)
        self.screen = pygame.display.set_mode((screenDim, screenDim))

    def draw(self):
        """

        For each object in self.objs, draw to the screen in reverse order of distance away from the camera.

        """

        self.screen.fill(self.background)

        o = self.__sortObjects()

        for x in o:
            x.draw(self.screen, self.pointMap, self.offset, self.rot)

    def __sortObjects(self):  # This method isn't perfect but works for the majority of scenarios
        """

        Use the centroid of triangles and the midpoints of lines to order by.

        """
        return sorted(self.objs, key=lambda element: element.centre(self), reverse=True)

    def adjustOffset(self, keys, dt):
        """

        Allows the camera to free fly around - q is vertically up, e is vertically down.
        Arrow keys move relative to the camera's rotation.

        """
        t = dt / 100
        if keys[pygame.K_UP]:
            self.offset[0] += t * cos(self.rot[0]) * cos(self.rot[1])
            self.offset[1] -= t * sin(self.rot[1])
            self.offset[2] += t * sin(self.rot[0]) * cos(self.rot[1])

        if keys[pygame.K_DOWN]:
            self.offset[0] -= t * cos(self.rot[0]) * cos(self.rot[1])
            self.offset[1] += t * sin(self.rot[1])
            self.offset[2] -= t * sin(self.rot[0]) * cos(self.rot[1])

        if keys[pygame.K_RIGHT]:
            self.offset[0] += t * cos(self.rot[0] + pi / 2)
            self.offset[2] += t * sin(self.rot[0] + pi / 2)
            
        if keys[pygame.K_LEFT]:
            self.offset[0] -= t * cos(self.rot[0] + pi / 2)
            self.offset[2] -= t * sin(self.rot[0] + pi / 2)

        if keys[pygame.K_q]:
            self.offset[1] += t

        if keys[pygame.K_e]:
            self.offset[1] -= t

    def adjustRotation(self, motion):
        """

        Given a list motion = [a, b], adjust the camera's rotation.
        Transformation of points is handled in __SceneObject.draw(), not here.


        """
        self.rot[0] += motion[0] / 100
        self.rot[1] += motion[1] / 100

        if self.rot[1] < - pi / 2:  # Fixing vertical rotation to stop camera flipping around
            self.rot[1] = - pi / 2

        if self.rot[1] > pi / 2:
            self.rot[1] = pi / 2
