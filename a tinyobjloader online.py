import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import *


if __name__ == "__main__":
    pygame.init()
    display = (1000,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(90, (display[0]/display[1]), 1, 100)

    glTranslatef(0.0,0.0, -10)

    # import file
    model = OBJ('model/a2_data/cube.obj')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        # draw model
        glPushMatrix()
        glTranslatef(10, 10, 10)
        model.render()
        glPopMatrix()
        
        pygame.display.flip()
        pygame.time.wait(10)
