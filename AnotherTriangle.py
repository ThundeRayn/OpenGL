import numpy as np
from OpenGL.GL import *
import glfw

glfw.init()
window = glfw.create_window(900, 700, "PyOpenGL Triangle", None,None)
glfw.set_window_pos(window, 200, 80)
glfw.make_context_current(window)

vertices = [-0.2, -0.2, 0.0,
             0.2, -0.2,0.0,
             0.0, 0.2, 0.0]

# list the color code here
colors = [0.5, 0.5, 0,
          0, 0.8, 0.9,
          0, 0.2, 1.0 ]

v = np.array (vertices, dtype = np.float32)
c = np.array (colors, dtype = np.float32)
# this will create a color-less triangle
glEnableClientState(GL_VERTEX_ARRAY)
glVertexPointer(3, GL_FLOAT, 0, v)
glEnableClientState(GL_COLOR_ARRAY)
glColorPointer(3, GL_FLOAT, 0, c)
# Now we will pour color for the animation's background
glClearColor(0.6, 0.8, 0.2,0.2)

while not glfw.window_should_close(window):
# this while loop will keep iterating all the functions below until the window is not closed
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
# creating rotation animated motion
    glRotatef(0.1, 1, 0 ,0)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glfw.swap_buffers(window)
glfw.terminate()
