from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


#--section1--#
def square():
    #declare four points
    glBegin(GL_QUADS) #begin the sketch
    glVertex2f(100,100) #Coordinates for the bottom left point
    glVertex2f(200,100) #Coordinates for the bottom right point
    glVertex2f(200,200) #Coordinates for the top right point
    glVertex2f(100,200) #Coordinates for the top left point
    glEnd() #Mark the end of drawing
    
#--interate--#
def iterate():
    glViewport(0, 0, 500,500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()
    
#--section2---#
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #remove everything from screen(i.e. display all white)
    glLoadIdentity()#Reset all graphic/shape's position
    iterate()
    glColor3f(1.0, 0.0, 3.0)#set color to pink
    square()#Draw a square using our function
    glutSwapBuffers()


#--section3--#
glutInit()                  #Initialize a glut instance which will allow us to customize our window
glutInitDisplayMode(GLUT_RGBA)
                            #Set the display mode to be colored
glutInitWindowSize(512,512) #Set the width and height of your window
glutInitWindowPosition(0,0) #Set the position at which the windows should appear
wind = glutCreateWindow("OpenGL Coding Practice")
                            #Give your window a title
glutDisplayFunc(showScreen) #Tell OpenGL to call the showScreen method continuously
glutIdleFunc(showScreen)    #Draw any graphics or shapes in the showScreen functionat all times
glutMainLoop()              #Keeps the windows created above displaying/running in a loop

#the square is now invisible cause the square has no color

