import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
from OpenGL import GL as gl

class App:
    def __init__(self):
        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)#create window
        self.clock = pg.time.Clock()
        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        #get alpha transparency working
        glEnable(GL_BLEND) #enable a blend function
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA) #standard function for alpha belnding
        #use shaders
        self.triangle = Triangle()
        self.shader = self.createShader("shaders/texture_vertex.txt", "shaders/texture_fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader,"imageTexture"),0)#you are sampling texture 0
        self.wood_texture = Material("gfx/cat_transparent.png")
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
            glUseProgram(self.shader)#use the rgiht shader
            self.wood_texture.use()
            glBindVertexArray(self.triangle.vao)#get the current model
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)#draw mode
            #lines/points/other structures, the point we want to start from(0),number of points to draw

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.triangle.destroy()
        self.wood_texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()


class Triangle:

    def __init__(self):

        # x, y, z, r, g, b, s, t(st is for texture pos)
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0 
        )
        #store vertices, float32 helps opengl to read
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1) #vertex array object, tell what does index mean-attributes
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1) #a vertex buffer object, buffer is a basic storage container
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)#bind the buffer
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes, self.vertices,GL_STATIC_DRAW)
        #tell how to use data, from data to graphic. store once, read many times

        #adding attributes in the vbo
        glEnableVertexAttribArray(0)#enable attribute 1:position
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(0))#how it lays out in vbo
        glEnableVertexAttribArray(1)#attribute 2:color
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(12))
        #index: 1 means color, 3 vertexs, gloating point desemos, each vertex has 6pt*4=24bytes, offset:where to begin to read the data
        #position is at the front, so it starts at 0
        #color starts at 12(before is position bytes)
        #we allocate the data here, so when we exit the program, we should free the memory
        glEnableVertexAttribArray(2)#add material here
        glVertexAttribPointer(2,2,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(24))

    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,))#there is only one obj
        glDeleteBuffers(1,(self.vbo,))#it could be a tuple or sth

class Material:
    def __init__(self,filepath):
        self.texture=glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)#address mode for ST. texture coordinate are stored in ST pair 
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)#S=0 right, S=1 left; T=0 is top, T=1 is buttom #repear means if you entered 1.5, you won't jump to another texture image
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)#when minimizing it, nearest shirnks it down
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)#when magnifiying it, linear keep it smooth
        #load the image
        image = pg.image.load(filepath).convert_alpha()#convert with alpha
        image_width, image_height = image.get_rect().size #what is the get rect mehotds?
        image_data = pg.image.tostring(image,"RGBA")
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,image_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    
    def use(self):
        glActiveTexture(GL_TEXTURE0) #opengl allows load multiple textures
        glBindTexture(GL_TEXTURE_2D,self.texture)
    
    def destroy(self):
        glDeleteTextures(1,(self.texture,))


if __name__ == "__main__":
    myApp = App()