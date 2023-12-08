import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from OpenGL import GL as gl
import tinyobjloader
from PIL import Image
import math

class Component:


    def __init__(self, position, eulers,up):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)

class Light:
    def __init__(self,position,direction,color,strength):
        self.position = np.array(position,dtype=np.float32)
        self.color = np.array(color,dtype=np.float32)
        self.direction = np.array(direction,dtype=np.float32)
        self.strength=strength
    
class Scene:

    def __init__(self):

        self.thetab = 0
        self.thetar = -math.pi/8
        self.thetag = 5 * math.pi/8
        self.lights =[
            Light(
                #position = [150 * math.sin(self.theta),100,150 * math.cos(self.theta)],
                position = [0,200,0],
                direction = [50 * math.sqrt(2) * math.cos(self.thetar),-200,50 * math.sqrt(2) * math.sin(self.thetar)],
                color = [1,0,0],
                strength = 2.0
            ),
            Light(
                position = [0,200,0],
                direction = [50 * math.sqrt(2) * math.cos(self.thetag),-200,50 * math.sqrt(2) * math.cos(self.thetag)],
                color = [0,1,0],
                strength = 2.0
            ),
            Light(
                position = [0,200,0],
                direction = [50 * math.sin(self.thetab),-200,50 * math.cos(self.thetab)],
                color = [0,0,1],
                strength = 2.0
            )
        ]

        self.timmy = Component(
            position=[0,80,0],
            eulers = [0,0,0],
            up=[0,1,0]
        )

    def update(self,rate):
        self.thetab += rate
        self.thetar += rate
        self.thetag += rate
        #for blue light
        self.lights[2].direction[0]= 50 * math.sin(self.thetab)
        self.lights[2].direction[1]= -200
        self.lights[2].direction[2]= 50 * math.cos(self.thetab)
        #for the red light
        self.lights[0].direction[0]= 50 * math.sqrt(2) * math.cos(self.thetab)
        self.lights[0].direction[1]= -200
        self.lights[0].direction[2]= -50 * math.sqrt(2) * math.sin(self.thetab)
        #for the red light
        self.lights[1].direction[0]= 50 * math.sqrt(2) * math.cos(self.thetag)
        self.lights[1].direction[1]= -200
        self.lights[1].direction[2]= -50 * math.sqrt(2) * math.sin(self.thetag)
        
        

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

            self.scene.update(0.05)

            self.renderer.render(self.scene)

            #timing
            #self.calculateFramerate()
        
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
        glClearColor(0.3, 0.4, 0.5, 1.0)
        glEnable (GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
        

        #create renderpasses and resources
        #load objects
        self.timmyMesh = Mesh("asset/timmy.obj","asset/timmy.png")
        self.bucketMesh= Mesh("asset/bucket.obj","asset/bucket.jpg")
        self.floorMesh= Mesh("asset/floor.obj","asset/floor.jpeg")

        #shaders
        self.shader = self.createShader("shaders/a3_3_v.txt", "shaders/a3_3_f.txt")
        self.renderPass = RenderPass(self.shader)
        
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
        glUseProgram(self.shader)

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
            near = 1, far = 1000, dtype=np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.colorLoc = glGetUniformLocation(self.shader, "object_color")
        
        self.lightLocation = {
            "position":[
                glGetUniformLocation(self.shader,f"Lights[{i}].position")
                for i in range(3)
            ],
            "direction":[
                glGetUniformLocation(self.shader,f"Lights[{i}].direction")
                for i in range(3)
            ],
            "color":[
                glGetUniformLocation(self.shader,f"Lights[{i}].color")
                for i in range(3)
            ],
            "strength":[
                glGetUniformLocation(self.shader,f"Lights[{i}].strength")
                for i in range(3)
            ]
        }
    
    def render(self, scene, engine):

        view_transform = pyrr.matrix44.create_look_at(
            eye = np.array([50,100,200],dtype=np.float32),
            target = np.array(scene.timmy.position,dtype=np.float32),
            up = np.array(scene.timmy.up, dtype = np.float32),dtype=np.float32
        )
        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_FALSE, view_transform)
        
        for i,light in enumerate(scene.lights):
            glUniform3fv(self.lightLocation["position"][i],1,light.position)
            glUniform3fv(self.lightLocation["direction"][i],1,light.direction)
            glUniform3fv(self.lightLocation["color"][i],1,light.color)
            glUniform1f(self.lightLocation["strength"][i],light.strength)
        
        #timmy
        glUniform3fv(self.colorLoc,1,engine.palette["COLOR"])
        modelTransform=pyrr.matrix44.create_identity(dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,modelTransform)
        glBindVertexArray(engine.timmyMesh.vao)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA, engine.timmyMesh.skin.width, engine.timmyMesh.skin.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, engine.timmyMesh.img_data)
        glDrawArrays(GL_TRIANGLES,0,engine.timmyMesh.vertex_count)
        
        #bucket
        glUniform3fv(self.colorLoc,1,engine.palette["COLOR"])
        modelTransform=pyrr.matrix44.create_identity(dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,modelTransform)
        glBindVertexArray(engine.bucketMesh.vao)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA, engine.bucketMesh.skin.width, engine.bucketMesh.skin.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, engine.bucketMesh.img_data)
        glDrawArrays(GL_TRIANGLES,0,engine.bucketMesh.vertex_count)
        
        
        #floor
        glUniform3fv(self.colorLoc,1,engine.palette["COLOR"])
        modelTransform=pyrr.matrix44.create_identity(dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,modelTransform)
        glBindVertexArray(engine.floorMesh.vao)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA, engine.floorMesh.skin.width, engine.floorMesh.skin.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, engine.floorMesh.img_data)
        glDrawArrays(GL_TRIANGLES,0,engine.floorMesh.vertex_count)
        
        glFlush()

    def destroy(self):
        glDeleteProgram(self.shader)

class Mesh:

    def __init__(self, filename,imagefile):
        # tinyobjloader
        reader = tinyobjloader.ObjReader()
        ret = reader.ParseFromFile(filename)
        attrib = reader.GetAttrib()

        # x, y, z, s, t, nx, ny, nz
        self.vertices = self.loadMesh(filename)
        self.vertex_count = len(self.vertices)//8
        self.vertices = np.array(self.vertices, dtype=np.float32)
        print(len(self.vertices)//8)#=13680

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

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        #load image
        self.skin=Image.open(imagefile)
        self.skin = self.skin.transpose(Image.FLIP_TOP_BOTTOM)
        self.img_data = self.skin.convert("RGBA").tobytes()

    
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
 
myApp = App(1024,768)
