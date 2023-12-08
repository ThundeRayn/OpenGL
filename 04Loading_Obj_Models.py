from curses.ascii import VT
import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr


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

        self.cube_mesh=Mesh("model/data_a2/cube.obj")

        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)

        #use shaders
        self.shader = self.createShader("shaders/trans_vertex.txt", "shaders/trans_fragment.txt")
        glUseProgram(self.shader)
        #get material
        glUniform1i(glGetUniformLocation(self.shader,"imageTexture"),0)#you are sampling texture 0
        self.wood_texture = Material("gfx/wooden_texture.png")
        #enable depth test
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)

        self.cube = Cube(
            position = [0,0,-15], #z=0 is in line of screen, -z (in front of the camera)
            eulers = [60,60,60] #pitch-x,roll-z,yaw-y
        )

        #using pyrr to generate the perspective projection matrix
        projection_transform=pyrr.matrix44.create_perspective_projection(
            fovy = 45.0, aspect = 640.0/480.0, #fovy:angle in the y, 45*2=90, aspect screen width over screen height
            near=0.1, far=1000, dtype=np.float32 #anything z<0.1,z>10 won't be draw, 
        )
        glUniformMatrix4fv( 
            glGetUniformLocation(self.shader,"projection"), #the location of projective uniform
            1,GL_FALSE,projection_transform #number of matrix, whether to transpose them, the actual arguments
        )

        #update our cube(so it rotate)
        self.modelMatrixLocation = glGetUniformLocation(self.shader,"model")
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

            #update cube - make euler rotation, 0x,1z,2y
            self.cube.eulers[2]+=0.25
            if self.cube.eulers[2] >360:
                self.cube.eulers[2] -= 360

            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)#use the rgiht shader

            #draw a cube
            #identity
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.eulers), dtype=np.float32
                )
            )#rotation

            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=self.cube.position, dtype=np.float32
                )                
            )#transformation

            glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,model_transform)
            self.wood_texture.use()
            glBindVertexArray(self.cube_mesh.vao)#get the current model
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)#draw mode
            #lines/points/other structures, the point we want to start from(0),number of points to draw

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        self.wood_texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Mesh:

    def __init__(self,filepath):
        # load .obj, x, y, z, s, t, nx, ny, nz
        self.vertices = self.loadMesh(filepath)
        self.vertex_count = len(self.vertices)// 8
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vao = glGenVertexArrays(1) #vertex array object, tell what does index mean-attributes
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1) #a vertex buffer object, buffer is a basic storage container
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)#bind the buffer
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes, self.vertices,GL_STATIC_DRAW)
        #tell how to use data, from data to graphic. store once, read many times

        #adding attributes in the vbo
        #position x,y,z
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(0))#how it lays out in vbo
        #texture s,t
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(12))
        #normals nx,ny,nz - not doing lighting here
        #glEnableVertexAttribArray(2)
        #glVertexAttribPointer(2,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(20))

    def loadMesh(self,filepath):
        vertices =[]
        v=[]#vertex
        vt = []#vertex textures
        vn = [] #vertex normals

        with open(filepath,"r") as f:
            #reading whole .obj file line by line
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]

                if flag == "v":
                    line = line.replace("v ","")
                    #[x,y,z]
                    line = line.split(" ")
                    l = [float(x) for x in line] #all the vertices
                    v.append(l)
                elif flag == "vt":
                    line = line.replace("vt ","")
                    #[s,t]
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag == "vn":
                    line = line.replace("vn ","")
                    #[nx,ny,nz]
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vn.append(l)
                elif flag == "f":
                    #face, three or more vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace('\n',"")
                    #[../../.., ../../.., ../../..]
                    line = line.split(" ")
                    faceVertices = []
                    faceTextures = []
                    faceNormals = []
                    for vertex in line:
                        #vertex = v/vt/vn
                        #[v,vt,vn]
                        l = vertex.split("/")
                        position = int(l[0])-1
                        faceVertices.append(v[position])
                        texture = int(l[1])-1
                        faceTextures.append(vt[texture])
                        normal = int(l[2]) -1
                        faceNormals.append(vn[normal])
                        #[0,1,2,3] ->[0,1,2,0,2,3]
                        triangles_in_face = len(line) - 2
                        vertex_order = []#check unpacked vertices
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)
                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)
                        for x in faceTextures[i]:
                            vertices.append(x)
                        for x in faceNormals[i]:
                            vertices.append(x)
                line = f.readline()
        return vertices

    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,))#there is only one obj
        glDeleteBuffers(1,(self.vbo,))#it could be a tuple or sth

class Cube:
    def __init__(self,position,eulers):
        self.position = np.array(position,dtype=np.float32)
        self.eulers = np.array(eulers,dtype=np.float32)#discuss later

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