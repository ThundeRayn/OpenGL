from OpenGL import GL as gl
import glfw
import ctypes
import sys


'''for capture screen shots'''
def dump_framebuffer_to_ppm(ppm_name, fb_width, fb_height):
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


screen_width, screen_height = 512, 512
ss_id = 0 # screenshot id

''' create window'''
if not glfw.init():
    sys.exit(1)
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
title = 'Assignment0'
window = glfw.create_window(screen_width, screen_height, title, None, None)
if not window:
    print('GLFW Window Failed')
    sys.exit(2)
glfw.make_context_current(window)
gl.glClearColor(0.3, 0.4, 0.5, 0)

'''create triangle vertex arrays and buffers'''
vertex_array_id = gl.glGenVertexArrays(1)
gl.glBindVertexArray(vertex_array_id)
vertex_data = [-0.8, -0.8, 0, #bottom left
               0.8, -0.8, 0, #bottom right
               0, 0.8, 0] # top mid
attr_id = 0
vertex_buffer = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)
array_type = (gl.GLfloat * len(vertex_data))
sizeof_float = ctypes.sizeof(ctypes.c_float)
gl.glBufferData(gl.GL_ARRAY_BUFFER,
                len(vertex_data) * sizeof_float,
                array_type(*vertex_data),
                gl.GL_STATIC_DRAW)
gl.glVertexAttribPointer(
    attr_id,  # attribute 0.
    3,  # components per vertex attribute
    gl.GL_FLOAT,  # type
    False,  # to be normalized?
    0,  # stride
    None  # array buffer offset
)
gl.glEnableVertexAttribArray(attr_id)

shaders = {
    gl.GL_VERTEX_SHADER: '''\
    #version 330 core
    layout(location = 0) in vec3 aPos;
    void main() {
        gl_Position = vec4(aPos, 1);
    }
''',
    gl.GL_FRAGMENT_SHADER: '''\
    #version 330 core
    out vec3 color;
    void main() {
      color = vec3(0.9,0.8,0.7);
    }
'''}

program_id = gl.glCreateProgram()
shader_ids = []
for shader_type, shader_src in shaders.items():
    shader_id = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader_id, shader_src)
    gl.glCompileShader(shader_id)
    # check if compilation was successful
    result = gl.glGetShaderiv(shader_id, gl.GL_COMPILE_STATUS)
    nlog = gl.glGetShaderiv(shader_id, gl.GL_INFO_LOG_LENGTH)
    if nlog:
        logmsg = gl.glGetShaderInfoLog(shader_id)
        print("Shader Error", logmsg)
        sys.exit(1)
    gl.glAttachShader(program_id, shader_id)
    shader_ids.append(shader_id)

gl.glLinkProgram(program_id)
result = gl.glGetProgramiv(program_id, gl.GL_LINK_STATUS)
nlog = gl.glGetProgramiv(program_id, gl.GL_INFO_LOG_LENGTH)
if nlog:
    logmsg = gl.glGetProgramInfoLog(program_id)
    print("Link Error", logmsg)
    sys.exit(1)
gl.glUseProgram(program_id)


while (
    glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and
    not glfw.window_should_close(window)
):

    #press key p will capture screen shot
    if glfw.get_key(window, glfw.KEY_P) == glfw.PRESS:
        print ("Capture Window ", ss_id)
        buffer_width, buffer_height = glfw.get_framebuffer_size(window)
        ppm_name = "Assignment0-ss" + str(ss_id) + ".ppm"
        dump_framebuffer_to_ppm(ppm_name, buffer_width, buffer_height)
        ss_id += 1

    #draw triangle
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
    glfw.swap_buffers(window)
    glfw.poll_events()

#release resource
for shader_id in shader_ids:
    gl.glDetachShader(program_id, shader_id)
    gl.glDeleteShader(shader_id)
gl.glUseProgram(0)
gl.glDeleteProgram(program_id)
