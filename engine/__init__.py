"""

3D rasterizer for simple projects.

To get started, create a Scene object with some other objects in it, such as Points, Lines and Triangles.
Create a Camera object to create a screen.
Instead of drawing each shape individually on the screen, call scene.draw().
Adjust scene.offset and scene.rot to make the camera move and rotate respectively.

Does not work with overlapping objects.

"""

from engine._obj import *
from engine._scene import *


def __test():
    """

    Demo function for the rasterizer.

    """
    import sys

    pygame.init()
    i = pygame.display.Info()

    grab = False

    pList = []

    for x in range(0, 10):
        for z in range(-5, 5):
            pList.append(Point(x, 2.5, z))

    scene = Scene(*pList,  # Grid of points above the camera
                  Triangle(Point(5, 5, 5),
                           Point(5, 5, 6),
                           Point(5, 4, 5),
                           col=(255, 0, 0)),

                  Sphere(5, 2.5, 2, 2, col=(255, 0, 155)),

                  Cube(Point(5, 0, 0), Point(5, 0, 1), Point(5, -1, 0), col=(255, 0, 0)),
                  screenDim=min(i.current_w, i.current_h) - 50)

    clock = pygame.time.Clock()

    lastMouseMotion = (0, 0)

    scene.screen.fill((255, 255, 255))

    while True:

        dt = clock.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.set_grab(False)
                    pygame.mouse.set_visible(True)
                    grab = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                grab = True

            elif event.type == pygame.MOUSEMOTION:
                if event.rel != (-1 * lastMouseMotion[0], -1 * lastMouseMotion[1]) and grab:
                    scene.adjustRotation(event.rel)
                    pygame.mouse.set_pos(scene.dim / 2, scene.dim / 2)
                    lastMouseMotion = event.rel

        keys = pygame.key.get_pressed()
        scene.adjustOffset(keys, dt)

        scene.draw()

        pygame.display.flip()


# Clearing up namespace

del ArgumentError


if __name__ == '__main__':
    __test()
