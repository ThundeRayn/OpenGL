import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from OpenGL import GL as gl
import copy

class Component:

    def __init__(self, position, eulers,up):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)

class Scene:

    def __init__(self):

        self.enemySpawnRate = 0.1

        self.face = Component(
            position = [0,100,0],
            eulers = [0, 0, 0],
            up = [0,1,0]
        )
        self.cube = Component(
            position = [0,0,0],
            eulers = [0, 0, 0],
            up = [0,1,0]
        )

class App:


    def __init__(self, screenWidth, screenHeight):

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.renderer = GraphicsEngine()

        self.scene = Scene()

        self.lastTime = pg.time.get_ticks()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0

        self.mainLoop()

    def mainLoop(self):
        ss_id = 0 #screenshot id
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                            #press key p will capture screen shot
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        print ("Capture Window ", ss_id)
                        buffer_width, buffer_height = 1024,768
                        ppm_name = "Assignment0-ss" + str(ss_id) + ".ppm"
                        self.dump_framebuffer_to_ppm(ppm_name, buffer_width, buffer_height)
                        ss_id += 1
            
            self.handleKeys()
            
            self.renderer.render(self.scene)

            #timing
            self.calculateFramerate()
        
        self.quit()

    def handleKeys(self):

        keys = pg.key.get_pressed()

    def calculateFramerate(self):

        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = max(1,int(1000.0 * self.numFrames/delta))
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1,framerate))
        self.numFrames += 1

    def dump_framebuffer_to_ppm(self,ppm_name, fb_width, fb_height):
        pixelChannel = 3
        pixels = gl.glReadPixels(0, 0, fb_width, fb_height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        fout = open(ppm_name, "w")
        fout.write('P3\n{} {}\n255\n'.format(int(fb_width), int(fb_height)))
        for i in range(0, fb_height):
            for j in range(0, fb_width):
                cur = pixelChannel * ((fb_height - i - 1) * fb_width + j)
                fout.write('{} {} {} '.format(int(pixels[cur]), int(pixels[cur+1]), int(pixels[cur+2])))
            fout.write('\n')
        fout.flush()
        fout.close()
    
    def quit(self):
        
        self.renderer.destroy()

class GraphicsEngine:

    def __init__(self):

        self.palette={
            "COLOR": np.array([0.8,0.7,0.6],dtype = np.float32)
        }

        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((1024,768), pg.OPENGL|pg.DOUBLEBUF)

        #initialise opengl
        glClearColor(0.3, 0.4, 0.5, 1)
        glEnable(GL_DEPTH_TEST|GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
        glEnable (GL_CULL_FACE)

        #create renderpasses and resources
        self.faceMesh = Mesh("model/data_a2/faces/base.obj")
        #self.cubeMesh = Mesh("model/data_a2/cube.obj")
        self.faces = FaceLoader()
        self.newExpression = NewFace(self.faceMesh,self.faces)
        shader = self.createShader("shaders/a2_v_try.txt", "shaders/a2_f_try.txt")
        self.renderPass = RenderPass(shader)
       
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def render(self, scene):

        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.renderPass.render(scene, self)

        pg.display.flip()

    def destroy(self):

        pg.quit()

class RenderPass:

    def __init__(self, shader):

        #initialise opengl
        self.shader = shader
        glUseProgram(self.shader)

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 60, aspect = 1024/768, 
            near = 0.1, far = 1000, dtype=np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.colorLoc = glGetUniformLocation(self.shader, "object_color")

    def render(self, scene, engine):

        glUseProgram(self.shader)

        view_transform = pyrr.matrix44.create_look_at(
            eye = np.array([0,100,100],dtype=np.float32),
            target = np.array(scene.face.position,dtype=np.float32),
            up = np.array(scene.face.up, dtype = np.float32),dtype=np.float32
        )
        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_FALSE, view_transform)

        #cube
        '''glUniform3fv(self.colorLoc,1,engine.palette["COLOR"])
        modelTransform=pyrr.matrix44.create_identity(dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,modelTransform)
        glBindVertexArray(engine.cubeMesh.vao)
        glDrawArrays(GL_TRIANGLES,0,engine.cubeMesh.vertex_count)'''

        #face
        '''glUniform3fv(self.colorLoc,1,engine.palette["COLOR"])
        modelTransform=pyrr.matrix44.create_identity(dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,modelTransform)
        glBindVertexArray(engine.faceMesh.vao)
        glDrawArrays(GL_TRIANGLES,0,engine.faceMesh.vertex_count)'''

        #new face0
        glUniform3fv(self.colorLoc,1,engine.palette["COLOR"])
        modelTransform=pyrr.matrix44.create_identity(dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,modelTransform)
        glBindVertexArray(engine.newExpression.vao)
        glDrawArrays(GL_TRIANGLES,0,engine.newExpression.vertex_count)

    def destroy(self):
        glDeleteProgram(self.shader)

class Mesh:

    def __init__(self, filename):

        # x, y, z, s, t, nx, ny, nz
        self.vertices = self.loadMesh(filename)
        self.vertex_count = len(self.vertices)//8
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
    
    def loadMesh(self, filename):

        #raw, unassembled data
        v = []
        vt = []
        vn = []
        
        #final, assembled and packed result
        vertices = []

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]
                if flag=="v":
                    #vertex
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                elif flag=="vt":
                    #texture coordinate
                    line = line.replace("vt ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag=="vn":
                    #normal
                    line = line.replace("vn ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vn.append(l)
                elif flag=="f":
                    #face, three or more vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    #get the individual vertices for each line
                    line = line.split(" ")
                    faceVertices = []
                    faceTextures = []
                    faceNormals = []
                    for vertex in line:
                        #break out into [v,vt,vn],
                        #correct for 0 based indexing.
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        faceVertices.append(v[position])
                        texture = int(l[1]) - 1
                        faceTextures.append(vt[texture])
                        normal = int(l[2]) - 1
                        faceNormals.append(vn[normal])
                    # obj file uses triangle fan format for each face individually.
                    # unpack each face
                    triangles_in_face = len(line) - 2

                    vertex_order = []
                    """
                        eg. 0,1,2,3 unpacks to vertices: [0,1,2,0,2,3]
                    """
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
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))
 
class FaceLoader:
    def __init__(self):
        #load face 0-34 here
        face0 = Mesh("model/data_a2/faces/0.obj")
        face1 = Mesh("model/data_a2/faces/1.obj")
        face2 = Mesh("model/data_a2/faces/2.obj")
        face3 = Mesh("model/data_a2/faces/3.obj")
        face4 = Mesh("model/data_a2/faces/4.obj")
        face5 = Mesh("model/data_a2/faces/5.obj")
        face6 = Mesh("model/data_a2/faces/6.obj")
        face7 = Mesh("model/data_a2/faces/7.obj")
        face8 = Mesh("model/data_a2/faces/8.obj")
        face9 = Mesh("model/data_a2/faces/9.obj")
        face10 = Mesh("model/data_a2/faces/10.obj")
        face11 = Mesh("model/data_a2/faces/11.obj")
        face12 = Mesh("model/data_a2/faces/12.obj")
        face13 = Mesh("model/data_a2/faces/13.obj")
        face14 = Mesh("model/data_a2/faces/14.obj")
        face15 = Mesh("model/data_a2/faces/15.obj")
        face16 = Mesh("model/data_a2/faces/16.obj")
        face17 = Mesh("model/data_a2/faces/17.obj")
        face18 = Mesh("model/data_a2/faces/18.obj")
        face19 = Mesh("model/data_a2/faces/19.obj")
        face20 = Mesh("model/data_a2/faces/20.obj")
        face21 = Mesh("model/data_a2/faces/21.obj")
        face22 = Mesh("model/data_a2/faces/22.obj")
        face23 = Mesh("model/data_a2/faces/23.obj")
        face24 = Mesh("model/data_a2/faces/24.obj")
        face25 = Mesh("model/data_a2/faces/25.obj")
        face26 = Mesh("model/data_a2/faces/26.obj")
        face27 = Mesh("model/data_a2/faces/27.obj")
        face28 = Mesh("model/data_a2/faces/28.obj")
        face29 = Mesh("model/data_a2/faces/29.obj")
        face30 = Mesh("model/data_a2/faces/30.obj")
        face31 = Mesh("model/data_a2/faces/31.obj")
        face32 = Mesh("model/data_a2/faces/32.obj")
        face33 = Mesh("model/data_a2/faces/33.obj")
        face34 = Mesh("model/data_a2/faces/34.obj")
        #create list here
        self.facelist=[
            face0,face1,face2,face3,face4,face5,face6,face7,face8,face9,face10,
            face11,face12,face13,face14,face15,face16,face17,face18,face19,face20,
            face21,face22,face23,face24,face25,face26,face27,face28,face29,face30,
            face31,face32,face33,face34]

        self.weight0= [0,0,0,0.64516,0.64516,0.35484,0.35484,2.90132e-09,2.90132e-09,0.739932,0.739932,2.77796e-09,2.77796e-09,0,0,0,0,0,0,0,0.0626911,0.0793342,0.0793342,0,0,0.0701688,0,1.12385,1.12385,0,0.0701688,0,0,1.76369,1.76369]
        self.weight1=[0,0,0.768983,0,0,0,0,0,0,0,0,0,0,0,0,0.999378,0.999378,0,0,0,0.401223,0.507739,0.507739,0,0,0.0701688,0,1.12385,1.12385,0,0.0701688,0,0,1.30073,1.30073]
        self.weight2=[0,0,0,0,0,0.823862,0.823862,0.176138,0.176138,0.939699,0.939699,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.0701688,0,1.12385,1.12385,0,0.0701688,0,0,0,0]
        self.weight3=[0,0,0,0,0.09,0.98,0.91,0.02,0,0.97,0.78,0.03,0.22,0,0,0,0,0.72,1,0.74,0.28,1,1,1,1,0,0,0,0,0.3,0.28,0.83,0.62,0,0]
        self.weight4=[0,0,0.832339,0.197422,0.167661,0,0,0,0,0,0,0,0,0,0,1.46853,1.46596,0,0,0,0,0,0,0.698089,0.698089,0.326277,0.299891,0,0,0,0,0,0,0,0]
        self.weight5=[0,0,0.437453,0.507972,0.562547,0,0,0,0,0.458765,0.506238,0.106683,0.0100309,0,0,0,0,1.07737,1.49706,1.50429,0.407081,1.95146,1.8032,1.25278,1.29567,0,0,0,0,0.55598,0.668959,0.662472,0.435237,0,0]
        self.weight6=[0,0,0,0,0.0886021,0.983432,0.911398,0.0165679,0,0.968577,0.777831,0.0314229,0.222169,0,0,0,0,0.721857,1.13796,0.738369,0.275525,1.10902,0.712409,1.04585,1.08238,0,0,0,0,0.296923,0.279794,0.884754,0.667099,0,0]
        self.weight7=[0,0,0,0.821842,0.821842,0.178158,0.178158,0,0,0,0,0,0,0,0,0.368324,0.368324,0.727662,0.60981,0.60981,0.413331,0.495321,0.495321,0,0,0,0,0.959612,0.975577,0.203271,0.479951,0,0,0.66063,0.66063]
        self.weight8= [0,0,0.567742,0,0,0,0,0,0,0.313347,0.313347,0,0,0,0,0,0,0,0,0,0,0,0.958764,0.200091,0,0.642503,0.316407,0.0494257,0.0646485,0,0,0.0441336,0.042033,0.0136918,0.0176112]
        self.weight9=[0.99533,0.99533,0.633821,0.366179,0.366179,0,0,0,0,0,0,0.305938,0.305938,0.694062,0.694062,0,0,0,0,0,0.00677602,0,0,0,0,0.435608,0.446517,0.00576265,0.021215,0,0,0.0130658,0.0114428,0,0]
        self.weight10=[0,0,0.514942,0,0,0,0,0,0,0.0534272,0.0534272,0,0,0,0,1.58,1.58,0.168069,0,0,0.444619,0,0.305247,0,0,0.715352,0.614297,0.0882583,0.114295,0,0,0.321887,0.301515,0.197721,0.256119]
        self.weight11=[0,0,0.567569,0.829958,0.432431,0.170042,0,0,0,0,0,0,0,0,0,0.219287,0.0902985,0.252216,0.0882965,0.0882965,0.421692,0.0777126,0.0777126,0,0,0.560673,0.527647,0.24814,0.271317,0,0,0.25222,0.229024,0.722435,0.790039]
        self.weightmy=[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #print(self.weight1)

class NewFace:
    def __init__(self,base,faces):

        self.vertices=copy.copy(base.vertices)
        for i in range(0,len(self.vertices)):
            for x in range(0,35):
                if i%float(8)==0.0 or i%float(8)==1.0 or i%float(8)==2.0:
                    self.vertices[i] = self.vertices[i] + faces.weight11[x]*(faces.facelist[x].vertices[i]-base.vertices[i])
        

        self.vertex_count = len(self.vertices)//8
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20)) 

myApp = App(1024,768)
