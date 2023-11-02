from abc import abstractmethod, ABCMeta
from math import sin, cos, sqrt

import pygame

from engine._error import *
from engine._scene import _OffsetHolder


class __SceneObject(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def draw(self, screen, pointMap, offset, rot):
        """

        Transform coordinates correctly, and draw the object to the screen.

        Coordinates are translated, then rotated, then projected to 2D, then drawn to the screen.
        All errors in the process must be caught.

        """
        pass

    @abstractmethod
    def centre(self, scene):
        """

        Return a numerical value of a measure of distance away from the camera.

        """
        pass


class Point(__SceneObject):
    def __init__(self, x, y, z, col=(0, 0, 0)):
        super().__init__()
        self.pos = (x, y, z)
        self.x = x
        self.y = y
        self.z = z
        self.col = col

    def draw(self, screen, pointMap, offset, rot):
        try:

            translatedCoordinates = (self.pos[0] - offset[0],
                                     self.pos[1] - offset[1],
                                     self.pos[2] - offset[2])

            rotatedCoordinatesY = (translatedCoordinates[0] * cos(rot[0]) + translatedCoordinates[2] * sin(rot[0]),
                                   translatedCoordinates[1],
                                   translatedCoordinates[2] * cos(rot[0]) - translatedCoordinates[0] * sin(
                                       rot[0]))  # Rotation in z axis

            fullRotatedCoordinates = (rotatedCoordinatesY[0] * cos(rot[1]) - rotatedCoordinatesY[1] * sin(rot[1]),
                                      rotatedCoordinatesY[0] * sin(rot[1]) + rotatedCoordinatesY[1] * cos(rot[1]),
                                      rotatedCoordinatesY[2])  # Rotation in y axis

            positionOnScreen = (fullRotatedCoordinates[2] / fullRotatedCoordinates[0],
                                fullRotatedCoordinates[1] / fullRotatedCoordinates[0])

            if fullRotatedCoordinates[0] <= 0:
                return

        except ZeroDivisionError:
            return

        # These coordinates must be between (-1 <= x <= 1, -1 <= y <= 1) to be on the screen
        if -1 <= positionOnScreen[0] <= 1 and -1 <= positionOnScreen[1] <= 1:
            coords = pointMap(positionOnScreen)
            coords = (round(coords[0]), round(coords[1]))  # Need integer arguments for blit

            pygame.draw.circle(screen, self.col, coords, 2)

    def centre(self, scene):
        return sum((self.pos[x] - scene.offset[x]) ** 2 for x in range(3))


class Line(__SceneObject):
    def __init__(self, *coords, col=(0, 0, 0), ends=(True, (0, 0, 0))):
        """

        coords should be a list of Point objects.

        """
        super().__init__()
        self.coords = list(coords)
        self.endInfo = ends

        if len(coords) != 2:
            raise ArgumentError('Incorrect number of points specified for Line')

        self.col = col

    def draw(self, screen, pointMap, offset, rot):
        coordListOnScreen = []
        for x in self.coords:  # Find the coordinates of each point on the screen and draw a polygon joining them.
            try:

                translatedCoordinates = (x.pos[0] - offset[0],
                                         x.pos[1] - offset[1],
                                         x.pos[2] - offset[2])

                rotatedCoordinatesY = (translatedCoordinates[0] * cos(rot[0]) + translatedCoordinates[2] * sin(rot[0]),
                                       translatedCoordinates[1],
                                       translatedCoordinates[2] * cos(rot[0]) - translatedCoordinates[0] * sin(
                                           rot[0]))  # Rotation in z axis

                fullRotatedCoordinates = (rotatedCoordinatesY[0] * cos(rot[1]) - rotatedCoordinatesY[1] * sin(rot[1]),
                                          rotatedCoordinatesY[0] * sin(rot[1]) + rotatedCoordinatesY[1] * cos(rot[1]),
                                          rotatedCoordinatesY[2])  # Rotation in y axis

                positionOnScreen = (fullRotatedCoordinates[2] / fullRotatedCoordinates[0],
                                    fullRotatedCoordinates[1] / fullRotatedCoordinates[0])

                if fullRotatedCoordinates[0] <= 0:
                    return

                coords = pointMap(positionOnScreen)
                coords = (round(coords[0]), round(coords[1]))  # Need integer arguments for blit

                # if -1 * 10e10 <= coords[0] <= 10e10 and -1 * 10e10 <= coords[1] <= 10e10:
                #     coordList.append(coords)  # Errors occur when coords go above magnitude of 10^10
                coordListOnScreen.append(coords)

            except ZeroDivisionError:
                pass

        try:
            pygame.draw.aaline(screen, self.col, coordListOnScreen[0], coordListOnScreen[1])
            if self.endInfo[0]:
                for x in coordListOnScreen:
                    pygame.draw.circle(screen, self.endInfo[1], x, 2)

        except IndexError:  # point not appended due to zero division error
            pass

    def centre(self, scene):
        midpoint = ((self.coords[0].pos[0] + self.coords[1].pos[0]) / 2,
                    (self.coords[0].pos[1] + self.coords[1].pos[1]) / 2,
                    (self.coords[0].pos[2] + self.coords[1].pos[2]) / 2)

        return sum((midpoint[x] - scene.offset[x]) ** 2 for x in range(3))


class Triangle(__SceneObject):
    def __init__(self, *coords, col=(0, 0, 0), lines=(True, (0, 0, 0)), corners=(True, (0, 0, 0))):
        """

        coords should be a list of Point objects.

        """
        super().__init__()
        self.coords = list(coords)
        if len(coords) != 3:
            raise ArgumentError('Incorrect number of points specified for Triangle')
        self.col = col
        self.cornersInfo = corners
        self.linesInfo = lines

    def draw(self, screen, pointMap, offset, rot):
        coordListOnScreen = []
        coordList3D = []
        for x in self.coords:  # Find the coordinates of each point on the screen and draw a polygon joining them.
            try:

                translatedCoordinates = (x.pos[0] - offset[0],
                                         x.pos[1] - offset[1],
                                         x.pos[2] - offset[2])

                rotatedCoordinatesY = (translatedCoordinates[0] * cos(rot[0]) + translatedCoordinates[2] * sin(rot[0]),
                                       translatedCoordinates[1],
                                       translatedCoordinates[2] * cos(rot[0]) - translatedCoordinates[0] * sin(
                                           rot[0]))  # Rotation in z axis

                fullRotatedCoordinates = (rotatedCoordinatesY[0] * cos(rot[1]) - rotatedCoordinatesY[1] * sin(rot[1]),
                                          rotatedCoordinatesY[0] * sin(rot[1]) + rotatedCoordinatesY[1] * cos(rot[1]),
                                          rotatedCoordinatesY[2])  # Rotation in y axis

                coordList3D.append(fullRotatedCoordinates)

                positionOnScreen = (fullRotatedCoordinates[2] / fullRotatedCoordinates[0],
                                    fullRotatedCoordinates[1] / fullRotatedCoordinates[0])

                if fullRotatedCoordinates[0] <= 0:
                    return

                coords = pointMap(positionOnScreen)
                coords = (round(coords[0]), round(coords[1]))  # Need integer arguments for blit

                # if -1 * 10e10 <= coords[0] <= 10e10 and -1 * 10e10 <= coords[1] <= 10e10:
                #     coordList.append(coords)  # Errors occur when coords go above magnitude of 10^10
                coordListOnScreen.append(coords)

            except ZeroDivisionError:
                pass

        if self.checkVisible(coordList3D):
            try:
                pygame.draw.polygon(screen, self.col, coordListOnScreen)  # Body of polygon done

            except (ValueError, TypeError):
                pass

            if self.linesInfo[0]:  # If lines are to be drawn
                try:
                    pygame.draw.aalines(screen, True, self.linesInfo[1], coordListOnScreen)

                except ValueError:
                    pass

            if self.cornersInfo[0]:  # If corners are to be drawn
                for x in self.coords:
                    x.draw(screen, pointMap, offset, rot)

    def centre(self, scene):
        c1 = self.coords[0]
        c2 = self.coords[1]
        c3 = self.coords[2]

        c1ToC2 = [c2.pos[x] - c1.pos[x] for x in range(3)]
        c1ToMedian = [c1ToC2[x] / 2 for x in range(3)]
        median = [c1.pos[x] + c1ToMedian[x] for x in range(3)]
        medianToC3 = [c3.pos[x] - median[x] for x in range(3)]
        medianToCentroid = [medianToC3[x] / 3 for x in range(3)]
        centroid = [median[x] + medianToCentroid[x] for x in range(3)]

        return sum((centroid[x] - scene.offset[x]) ** 2 for x in range(3))

    @staticmethod
    def getNormal(coords):
        c1 = coords[0]
        c2 = coords[1]
        c3 = coords[2]

        C1ToC2 = [(c2[x] - c1[x]) for x in range(3)]
        C1ToC3 = [(c3[x] - c1[x]) for x in range(3)]  # Two vectors on the surface of the triangle

        normal = [C1ToC2[2] * C1ToC3[1] - C1ToC2[1] * C1ToC3[2],
                  C1ToC2[0] * C1ToC3[2] - C1ToC2[2] * C1ToC3[0],
                  C1ToC2[1] * C1ToC3[0] - C1ToC2[0] * C1ToC3[1]]  # Cross product

        return normal

    @staticmethod
    def checkVisible(coords):
        """

        Find vectors along the surface.
        Cross product to create normal to the surface.
        Find the vector from the centroid of the triangle to the camera.
        If the dot product is negative, return False, else True.

        """

        c1 = coords[0]

        normal = Triangle.getNormal(coords)

        cornerToCamera = [-c1[x] for x in range(3)]

        dot = sum(normal[x] * cornerToCamera[x] for x in range(3))

        return dot >= 0


class Sphere(__SceneObject):
    def __init__(self, x, y, z, r, col=(0, 0, 0), outline=(True, (0, 0, 0))):
        super().__init__()
        self.pos = (x, y, z)
        self.radius = r
        self.col = col
        self.outline = outline

    def draw(self, screen, pointMap, offset, rot):
        try:

            translatedCoordinates = (self.pos[0] - offset[0],
                                     self.pos[1] - offset[1],
                                     self.pos[2] - offset[2])

            rotatedCoordinatesY = (translatedCoordinates[0] * cos(rot[0]) + translatedCoordinates[2] * sin(rot[0]),
                                   translatedCoordinates[1],
                                   translatedCoordinates[2] * cos(rot[0]) - translatedCoordinates[0] * sin(
                                       rot[0]))  # Rotation in z axis

            fullRotatedCoordinates = (rotatedCoordinatesY[0] * cos(rot[1]) - rotatedCoordinatesY[1] * sin(rot[1]),
                                      rotatedCoordinatesY[0] * sin(rot[1]) + rotatedCoordinatesY[1] * cos(rot[1]),
                                      rotatedCoordinatesY[2])  # Rotation in y axis

            positionOnScreen = (fullRotatedCoordinates[2] / fullRotatedCoordinates[0],
                                fullRotatedCoordinates[1] / fullRotatedCoordinates[0])

            if fullRotatedCoordinates[0] <= 0:
                return

        except ZeroDivisionError:
            return

        coords = pointMap(positionOnScreen)
        coords = (round(coords[0]), round(coords[1]))  # Need integer arguments for blit

        radius = round(pointMap((0, 1))[0] * self.radius / (2 * fullRotatedCoordinates[0]))

        pygame.draw.circle(screen, self.col, coords, radius)

        if self.outline[0]:
            pygame.draw.circle(screen, self.outline[1], coords, radius, 1)

    def centre(self, scene):
        return sum((self.pos[x] - scene.offset[x]) ** 2 for x in range(3))


class Cube(__SceneObject):
    def __init__(self, topEdge1, topEdge2, leftEdge, col=(0, 0, 0), lines=(True, (0, 0, 0)),
                 corners=(True, (0, 0, 0))):
        """

        topEdge and leftEdge variables should be point objects defining coordinates of the top and left edges.
        Viewing from the front face:

        topEdge1 -------------------topEdge2
           |                           |
           |                           |
           |                           |
           |                           |
        leftEdge ---------------------

        """
        super().__init__()
        topEdgeLength = sqrt(sum((topEdge1.pos[x] - topEdge2.pos[x]) ** 2 for x in range(3)))
        leftEdgeLength = sqrt(sum((topEdge1.pos[x] - leftEdge.pos[x]) ** 2 for x in range(3)))

        if topEdgeLength != leftEdgeLength:
            raise ArgumentError('Unequal side lengths for Cube.')

        # topEdgeLength == leftEdgeLength

        topEdgeToLeftEdge = [leftEdge.pos[x] - topEdge1.pos[x] for x in range(3)]
        topEdge1ToTopEdge2 = [topEdge2.pos[x] - topEdge1.pos[x] for x in range(3)]

        if sum(topEdgeToLeftEdge[x] * topEdge1ToTopEdge2[x] for x in range(3)) != 0:
            raise ArgumentError('Non-right angle between the top and left edges.')

        """
        
        We know that for two vectors a and b, axb = |a||b|n*sin(theta) where n is a unit vector perpendicular to both
        a and b.
        
        By the right hand rule, if we set a = topEdge1ToTopEdge2 and b = topEdgeToLeftEdge and divide by topEdgeLength,
        We get the vector from any coordinate on the front face to the corresponding one on the back face since sin90=1
        (|a| * n)
        
        """

        frontFacetoBackFace = [(topEdge1ToTopEdge2[1] * topEdgeToLeftEdge[2] - topEdge1ToTopEdge2[2] *
                               topEdgeToLeftEdge[1]) / topEdgeLength,
                               (topEdge1ToTopEdge2[2] * topEdgeToLeftEdge[0] - topEdge1ToTopEdge2[0] *
                               topEdgeToLeftEdge[2]) / topEdgeLength,
                               (topEdge1ToTopEdge2[0] * topEdgeToLeftEdge[1] - topEdge1ToTopEdge2[1] *
                               topEdgeToLeftEdge[0]) / topEdgeLength]
        # topEdge1ToTopEdge2 crossed with topEdgeToLeftEdge, scaled to the magnitude of topEdgeLength

        frontFace = [topEdge1.pos, topEdge2.pos, tuple(topEdge2.pos[x] + topEdgeToLeftEdge[x] for x in range(3)),
                     leftEdge.pos]  # Front face

        backFace = [tuple(x[y] + frontFacetoBackFace[y] for y in range(3)) for x in frontFace]

        vertices = frontFace + backFace

        self.midpoint = [(vertices[0][x] + vertices[6][x]) / 2 for x in range(3)]

        """
        
        From the order in this list, sets of indexes making valid triangles are:
        0, 1, 3 Front face
        1, 2, 3
        
        1, 5, 2 Right face
        5, 6, 2
        
        4, 0, 7 Left face
        0, 3, 7
        
        4, 5, 0 Top face
        5, 1, 0
        
        3, 2, 7 Bottom face
        2, 6, 7
        
        5, 4, 6 Back face
        4, 7, 6
        
        """

        self.objs = []

        vertexList = [(0, 1, 3),
                      (1, 2, 3),
                      (1, 5, 2),
                      (5, 6, 2),
                      (4, 0, 7),
                      (0, 3, 7),
                      (4, 5, 0),
                      (5, 1, 0),
                      (3, 2, 7),
                      (2, 6, 7),
                      (5, 4, 6),
                      (4, 7, 6)]

        for x in vertexList:
            self.objs.append(Triangle(*[Point(*vertices[x[y]]) for y in range(3)],
                                      col=col, lines=(False, None), corners=(False, None)))

        lineList = [(0, 1),
                    (1, 2),
                    (2, 3),
                    (3, 0),
                    (0, 4),
                    (1, 5),
                    (2, 6),
                    (3, 7),
                    (4, 5),
                    (5, 6),
                    (6, 7),
                    (7, 4)]

        if lines[0]:
            for x in lineList:
                self.objs.append(Line(Point(*vertices[x[0]]), Point(*vertices[x[1]]), col=lines[1], ends=(False, None)))

        if corners[0]:
            for x in vertices:
                self.objs.append(Point(*x, col=corners[1]))

        self.col = col
        self.linesInfo = lines
        self.cornersInfo = corners

    def centre(self, scene):

        return sum((self.midpoint[x] - scene.offset[x]) ** 2 for x in range(3))

    def draw(self, screen, pointMap, offset, rot):
        s = _OffsetHolder(offset)
        for x in sorted(self.objs, key=lambda element: element.centre(s), reverse=True):
            x.draw(screen, pointMap, offset, rot)


COMPOSITE = (Triangle,)
