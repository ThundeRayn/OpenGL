import pygame as pg
from OpenGL.GL import *

class App:

    def __init__(self):

        #initialize python
        pg.init()
        pg.display.set_mode((640,480),pg.OPENGL|pg.DOUBLEBUF)#new window
        self.clock = pg.time.Clock()#control the frame

        #initialize opengl
        glClearColor(0.1,0.2,0.2,1)#RGB% Alpha%
        self.mainLoop()


    def mainLoop(self):

        running = True
        while(running):
            #check events
            for event in pg.event.get():
                if(event.type==pg.QUIT):
                    running = False
                    
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT) #clear color buffer
            pg.display.flip()

            #timing
            self.clock.tick(60) #60 frame per second
        self.quit()

    def quit(self):
        pg.quit()

if __name__ == "__main__":
    myApp = App() #what does this mean?

