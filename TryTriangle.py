
import numpy as np
from OpenGL.GL import *
import glfw

glfw.init() #for initialization, so we can access glfw fucntions

### ----creating a window size having 900 as width and 700 as height
window = glfw.create_window(900,700, "PyOpenGL Triangle", None, None)
glfw.set_window_pos(window, 200, 80) #the window here is window name
glfw.make_context_current(window) #accept window augment relating to the current context


vertices = [-0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
            0.0, 0.5, 0.0]
v = np.array(vertices, dtype = np.float32)#???
# the vertices value indicates three points, representing the point of triangle


### ----this will draw a colorless triangle
glEnableClientState(GL_VERTEX_ARRAY) #???enable client-side competences
glVertexPointer(3, GL_FLOAT,0,v)  #???


### ----this will set a color for your background
glClearColor(255,180,0,0) #help in setting the background color,RGBA(A:alpha)???

while not glfw.window_should_close(window):
    #create a loop execute until the window creation gets terminated
    glfw.poll_events() #check for the events triggered to the window system???
    glClear(GL_COLOR_BUFFER_BIT) #Cleanning the screen every time the loop executes??? Assure nothing on the screen prior to the rendering of graphics
    glDrawArrays(GL_TRIANGLES,0,3)#put the vectorized graphics in consecutive pixels???
    glfw.swap_buffers(window) #???
    
glfw.terminate() #terminate the loop and creation for vecter graphics ???

#I don feel like I learned anything!
#cannot understand any lines 
