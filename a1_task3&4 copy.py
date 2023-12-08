from math import radians
import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from OpenGL import GL as gl


class App:
    day = 0
    def __init__(self):
        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((1024,768), pg.OPENGL|pg.DOUBLEBUF)#create window
        self.clock = pg.time.Clock()
        #initialise opengl
        glClearColor(0.3, 0.4, 0.5, 1)

        #enable depth test
        glEnable(GL_DEPTH_TEST)

        self.cube_mesh=CubeMesh()

        #use shaders
        self.shader = self.createShader("shaders/a1cubet_v.txt", "shaders/a1cubet_f.txt")
        glUseProgram(self.shader)

        #using pyrr to generate the perspective projection matrix
        projection_transform=pyrr.matrix44.create_perspective_projection(
            fovy = 30, aspect = 4/3, #fovy:angle in the y, 45*2=90, aspect screen width over screen height
            near=50, far=1000, dtype=np.float32 #anything z<0.1,z>10 won't be draw, 
        )
        glUniformMatrix4fv( 
            glGetUniformLocation(self.shader,"projection"), #the location of projective uniform
            1,GL_FALSE,projection_transform #number of matrix, whether to transpose them, the actual arguments
        ) 

        #update our cube(so it rotate)
        self.modelMatrixLocation = glGetUniformLocation(self.shader,"model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader,"view")

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
        ss_id = 0 #screenshot id
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False

                #press key p will capture screen shot
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        print ("Capture Window ", ss_id)
                        buffer_width, buffer_height = 1024,768
                        ppm_name = "Assignment0-ss" + str(ss_id) + ".ppm"
                        self.dump_framebuffer_to_ppm(ppm_name, buffer_width, buffer_height)
                        ss_id += 1
            
            #update day
            self.day+=1/24
            
            self.cube1 = Cube(
            position = [0,0,0], #z=0 is in line of screen, -z (in front of the camera)
            eulers = [0,0,self.get_sun_rotate_angle_around_itself(self.day)], #pitch-x,roll-z,yaw-y
            euler = [0,0,0]
            )
            self.cube2 = Cube(
                position = [20,0,0], #z=0 is in line of screen, -z (in front of the camera)
                eulers = [0,23.4,self.get_earth_rotate_angle_around_itself(self.day)-self.get_earth_rotate_angle_around_sun(self.day)], #pitch-x,roll-z,yaw-y
                euler = [0,0,self.get_earth_rotate_angle_around_sun(self.day)]
            )
            self.cube3 = Cube(
                position = [30,0,0], #z=0 is in line of screen, -z (in front of the camera)
                eulers = [0,0,self.get_moon_rotate_angle_around_itself(self.day)-self.get_moon_rotate_angle_around_earth(self.day)], #pitch-x,roll-z,yaw-y
                euler = [0,0,self.get_moon_rotate_angle_around_earth(self.day)]
            )

            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)#use the rgiht shader
 
            #view =self.get_earth_centre(self.get_earth_rotate_angle_around_sun(self.day))
            view = self.get_moon_centre(self.cube3.euler[2],self.cube2.euler[2])
            cam=[50,50,100]
            #view=[0,0,0]
            #draw three cubes here '''self.cube2.euler'''
            self.draw_cube(4,self.cube1.position,self.cube1.eulers,cam,view,[0,1,0],self.cube1.euler)
            self.draw_cube(2.5,self.cube2.position,self.cube2.eulers,cam,view,[0,1,0],self.cube2.euler)
            self.draw_moon(self.cube3.eulers[2],self.cube3.euler[2],self.cube2.euler,cam,view,[0,1,0])

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def draw_cube(self, int_scale,pos,eul,eyepos,tarpos,uppos,eul_around):
            #draw a cube
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1 = model_transform,
                m2 = pyrr.matrix44.create_from_scale(scale = np.array([int_scale,int_scale,int_scale],dtype=np.float32))
            )#scale
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_y_rotation(
                    theta=np.radians(eul[2]), dtype=np.float32
                )
            )#rotation itself
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians([0,eul[1],0]), dtype=np.float32
                )
            )#rotation for earth (the angle of 23.4)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=pos, dtype=np.float32
                )                
            )#transformation
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_y_rotation(
                    theta=np.radians(eul_around[2]), dtype=np.float32
                )
            )#rotation around [0,0,0]
            view_transform = pyrr.matrix44.create_look_at(
                eye = np.array(eyepos,dtype = np.float32),
                target = np.array(tarpos,dtype = np.float32),
                up = np.array(uppos,dtype = np.float32),dtype = np.float32
            )

            glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,model_transform)
            glUniformMatrix4fv(self.viewMatrixLocation,1,GL_FALSE,view_transform)
            glBindVertexArray(self.cube_mesh.vao)#get the current model
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)#draw mode

    def draw_moon(self,eul,eul_a_earth,eul_around,eyepos,tarpos,uppos):
        # I merge sun and earth together, but moon are way too different so I create a new func
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1 = model_transform,
                m2 = pyrr.matrix44.create_from_scale(scale = np.array([1.5,1.5,1.5],dtype=np.float32))
            )#scale
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_y_rotation(
                    theta=np.radians(eul), dtype=np.float32
                )
            )#rotation itself
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=[10,0,0], dtype=np.float32
                )                
            )#transformation
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_y_rotation(
                    theta=np.radians(eul_a_earth), dtype=np.float32
                )
            )#rotation around earth (rotate the whole obj)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=[20,0,0], dtype=np.float32
                )
            )#transformation rotating around earth moon to right pos
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(eul_around), dtype=np.float32
                )
            )#rotation around [0,0,0]
            view_transform = pyrr.matrix44.create_look_at(
                eye = np.array(eyepos,dtype = np.float32),
                target = np.array(tarpos,dtype = np.float32),
                up = np.array(uppos,dtype = np.float32),dtype = np.float32
            )

            glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,model_transform)
            glUniformMatrix4fv(self.viewMatrixLocation,1,GL_FALSE,view_transform)
            glBindVertexArray(self.cube_mesh.vao)#get the current model
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)#draw mode

            return 0

    def get_earth_centre(self,angle):
        vec_rotation = pyrr.matrix33.create_from_y_rotation(
            theta=np.radians(angle),dtype=np.float32
        )
        pos= pyrr.matrix33.apply_to_vector(
            mat = vec_rotation,
            vec=[20,0,0]
        )
        return pos

    def get_moon_centre(self,angle,angle_earth):
        vec_rotation = pyrr.matrix33.create_from_y_rotation(
            theta=np.radians(angle),dtype=np.float32
        )
        pos1= pyrr.matrix33.apply_to_vector(
            mat = vec_rotation,
            vec=[10,0,0]
        )#around y roate ar r=10

        module = pyrr.matrix44.create_from_translation(
            vec=[20,0,0],dtype=np.float32
        )
        pos2 = pyrr.matrix44.apply_to_vector(
            mat= module,
            vec = pos1
        )#translate to 30

        vec_rotation = pyrr.matrix44.create_from_y_rotation(
            theta=np.radians(angle_earth),dtype=np.float32
        )
        pos3= pyrr.matrix44.apply_to_vector(
            mat = vec_rotation,
            vec= pos2
        )#rotate around earth
        return pos3

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
    
    def get_sun_rotate_angle_around_itself(self,day):
        exulerz=0
        exulerz=day*(-360/27)
        return exulerz

    def get_earth_rotate_angle_around_sun(self,day):
        exulerz=0
        exulerz=day*(-360/365)
        return exulerz

    def get_earth_rotate_angle_around_itself(self,day):
        exulerz=0
        exulerz=day*(-360)
        return exulerz

    def get_moon_rotate_angle_around_earth(self,day):
        exulerz=0
        exulerz=day*(-360/28)
        return exulerz

    def get_moon_rotate_angle_around_itself(self,day):
        exulerz=0
        exulerz=day*(-360/28)
        return exulerz

    def quit(self):
        self.cube_mesh.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class CubeMesh:

    def __init__(self):
        self.vertices = (
                -1, -1, -1, 1, 0, 0,
                 1, -1, -1, 1, 0, 0,
                 1,  1, -1, 1, 0, 0,#a triangle mesh on back

                 1,  1, -1, 1, 0, 0,
                -1,  1, -1, 1, 0, 0,
                -1, -1, -1, 1, 0, 0,#another mesh on back

                -1, -1,  1, 1, 0, 1,
                 1, -1,  1, 1, 0, 1,
                 1,  1,  1, 1, 0, 1,#font1

                 1,  1,  1, 1, 0, 1,
                -1,  1,  1, 1, 0, 1,
                -1, -1,  1, 1, 0, 1,#font2

                -1,  1,  1, 0, 1, 0,
                -1,  1, -1, 0, 1, 0,
                -1, -1, -1, 0, 1, 0, #left1

                -1, -1, -1, 0, 1, 0,
                -1, -1,  1, 0, 1, 0,
                -1,  1,  1, 0, 1, 0, #left2

                 1,  1,  1, 1, 1, 0,
                 1,  1, -1, 1, 1, 0,
                 1, -1, -1, 1, 1, 0, #right1

                 1, -1, -1, 1, 1, 0,
                 1, -1,  1, 1, 1, 0,
                 1,  1,  1, 1, 1, 0, #right2

                -1, -1, -1, 0, 0, 1,
                 1, -1, -1, 0, 0, 1,
                 1, -1,  1, 0, 0, 1, #bottom1

                 1, -1,  1, 0, 0, 1,
                -1, -1,  1, 0, 0, 1,
                -1, -1, -1, 0, 0, 1, #bottom2

                -1,  1, -1, 0, 1, 1,
                 1,  1, -1, 0, 1, 1,
                 1,  1,  1, 0, 1, 1, #top1

                 1,  1,  1, 0, 1, 1,
                -1,  1,  1, 0, 1, 1,
                -1,  1, -1, 0, 1, 1, #top2
            )
        #store vertices, float32 helps opengl to read

        self.vertex_count = len(self.vertices)// 6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1) #vertex array object, tell what does index mean-attributes
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1) #a vertex buffer object, buffer is a basic storage container
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)#bind the buffer
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes, self.vertices,GL_STATIC_DRAW)
        #tell how to use data, from data to graphic. store once, read many times

        #adding attributes in the vbo
        glEnableVertexAttribArray(0)#enable attribute 1:position
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(0))#how it lays out in vbo
        #texture
        glEnableVertexAttribArray(1)#add material here
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(12))

    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,))#there is only one obj
        glDeleteBuffers(1,(self.vbo,))#it could be a tuple or sth

class Cube:
    def __init__(self,position,eulers,euler):
        self.position = np.array(position,dtype=np.float32)
        self.eulers = np.array(eulers,dtype=np.float32)#discuss later
        self.euler = np.array(euler,dtype=np.float32)#discuss later

if __name__ == "__main__":
    myApp = App()