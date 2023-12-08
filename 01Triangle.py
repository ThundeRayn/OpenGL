import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
from OpenGL import GL as gl

class App:
    def __init__(self):
        #initialise pygame
        pg.init()
        #get attributes -- For what is here????
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)#create window
        self.clock = pg.time.Clock()
        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        #use shaders
        self.triangle = Triangle()
        self.shader = self.createShader("shaders/_vertex.txt", "shaders/_fragment.txt")
        glUseProgram(self.shader)
        self.mainLoop()
    
    def createShader(self, vertexFilepath, fragmentFilepath):
        #open them in read mode
        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()

        #compile each of the individual mode
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def mainLoop(self):
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)

            #press key p will capture screen shot
        #if glfw.get_key(window, glfw.KEY_P) == glfw.PRESS:
        #    print ("Capture Window ", ss_id)
        #    buffer_width, buffer_height = glfw.get_framebuffer_size(window)
        #    ppm_name = "Assignment0-ss" + str(ss_id) + ".ppm"
        #    self.dump_framebuffer_to_ppm(ppm_name, buffer_width, buffer_height)
        #    ss_id += 1

            #draw a triangle
            glBindVertexArray(self.triangle.vao)#get the current model
            glUseProgram(self.shader)#use the rgiht shader
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)#draw mode
            #lines/points/other structures, the point we want to start from(0),number of points to draw

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.triangle.destroy()
        glDeleteProgram(self.shader)
        pg.quit()


class Triangle:

    def __init__(self):

        # x, y, z, r, g, b
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        )
        #store vertices, float32 helps opengl to read
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1) #vertex array object, tell what does index mean-attributes
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1) #a vertex buffer object, buffer is a basic storage container
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)#bind the buffer???
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes, self.vertices,GL_STATIC_DRAW)
        #tell how to use data, from data to graphic. store once, read many times

        #adding attributes in the vbo
        glEnableVertexAttribArray(0)#enable attribute 1:position
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(0))#how it lays out in vbo
        glEnableVertexAttribArray(1)#attribute 2:color
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(12))
        #index: 1 means color, 3 vertexs, gloating point desemos, each vertex has 6pt*4=24bytes, offset:where to begin to read the data
        #position is at the front, so it starts at 0
        #color starts at 12(before is position bytes)
        #we allocate the data here, so when we exit the program, we should free the memory

    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,))#there is only one obj
        glDeleteBuffers(1,(self.vbo,))#it could be a tuple or sth

if __name__ == "__main__":
    myApp = App()