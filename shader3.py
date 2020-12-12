from OpenGL.GL import *
from OpenGL.GLUT import *
from random import random
import ctypes
import time
from PIL import Image
import pygame
import numpy
# Треугольники во весь экран

point_vertex1 = [[1.0, -1.0, 0.0], [1.0, 1.0, 0], [-1.0, -1.0, 0]]
point_vertex2 = [[-1.0, 1.0, 0.0], [-1.0, -1.0, 0], [1.0, 1.0, 0]]
xOrigin = 0.0



def read_texture(filename =r'C:\Users\Gz-E\Desktop\OpenGL\anvil_top_damaged_0.png'):
    img = Image.open(filename)
    img_data = numpy.array(list(img.getdata()), numpy.int8)
    texture_id = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return texture_id

def specialkeys2(key, x, y):
    if key == GLUT_KEY_UP:
        fog_on = glGetUniformLocation(program, "flag")
        glUniform1f(fog_on, 10.0)
    if key == GLUT_KEY_DOWN:
        fog_off = glGetUniformLocation(program, "flag")
        glUniform1f(fog_off, -10.0)


def specialkeys(button, state, x, y):
    global xOrigin
    iMouse = glGetUniformLocation(program, "iMouse")
    if button == GLUT_LEFT_BUTTON:
        if (state == GLUT_UP):
            glUniform2f(iMouse, x, y)
            xOrigin = -1.0
        else:
            xOrigin = x


def mouseMove(x, y):
    global xOrigin
    iMouse = glGetUniformLocation(program, "iMouse")
    if xOrigin >= 0.0:
        glUniform2f(iMouse, x, y)


def create_shader(shader_type, sourse):
    # empty_shader
    shader = glCreateShader(shader_type)
    # text -> shader_prog
    glShaderSource(shader, sourse)
    # compile_shder
    glCompileShader(shader)

    return shader


Time = time.time()


def calc(x):
    global Time
    arg = time.time() - Time
    iTime = glGetUniformLocation(program, "iTime")
    glUniform1f(iTime, arg)
    glutTimerFunc(10, calc, 0)


def draw():
    glClear(GL_COLOR_BUFFER_BIT)

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, point_vertex1)

    glDrawArrays(GL_TRIANGLES, 0, 3)

    glVertexPointer(3, GL_FLOAT, 0, point_vertex2)

    glDrawArrays(GL_TRIANGLES, 0, 3)

    glDisableClientState(GL_VERTEX_ARRAY)
    glutSwapBuffers()


glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)

glutInitWindowSize(512, 512)

glutInitWindowPosition(0, 0)

glutInit(sys.argv)

glutCreateWindow(b"ShaderWindow")

glutDisplayFunc(draw)

glutIdleFunc(draw)
glutSpecialFunc(specialkeys2)
glutMouseFunc(specialkeys)
glutMotionFunc(mouseMove)

glClearColor(0, 0, 0, 1)

vertex = create_shader(GL_VERTEX_SHADER, """

void main(){
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}""")

fragment = create_shader(GL_FRAGMENT_SHADER, """


uniform float iTime;
uniform vec2 iMouse;
uniform vec2 iResolution;
uniform float flag;
uniform sampler2D iChannel0;
struct Quad {
    vec3 pos[4];
    vec3 color;
    vec3 normal;
};

const float FAR_INF = 1e10;
const float EPS = 1e-3;
const float PI = 3.14159265359;

float ray_triangle_intersection(Quad q, vec3 origin, vec3 dir) {

    float normalViewAngle = dot(dir, q.normal);
    if (abs(normalViewAngle) < EPS)
        return FAR_INF;
    float d = dot(q.pos[0] - origin, q.normal) / normalViewAngle;
    if (d < 0.0)
        return FAR_INF;
    vec3 hitPos = origin + dir * d;
    vec3 edges[4] = vec3[4](
        q.pos[1] - q.pos[0],
        q.pos[2] - q.pos[1],
        q.pos[3] - q.pos[2],
        q.pos[0] - q.pos[3]
    );
    float square = length(cross(edges[0], edges[1])) + length(cross(edges[2], edges[3]));
    vec3 toHitVecs[4] = vec3[4](
        hitPos - q.pos[0],
        hitPos - q.pos[1],
        hitPos - q.pos[2],
        hitPos - q.pos[3]
    );
    float testSq[4] = float[4](
        length(cross(toHitVecs[0], edges[0])),
        length(cross(toHitVecs[1], edges[1])),
        length(cross(toHitVecs[2], edges[2])),
        length(cross(toHitVecs[3], edges[3]))
    );
    if (abs(square - testSq[0] - testSq[1] - testSq[2] - testSq[3]) < EPS)
        return d;
    return FAR_INF;
}
float pow2(float x) { return x * x; }
vec3 getLightSpecular(Quad light, vec3 worldPos, vec3 viewVec, vec3 normal, float specFactor) {
    vec3 r = reflect(viewVec, normal);
    float sp = 0.0;
    for (int i = 0; i < 4; ++i) {
        vec3 vi = normalize(light.pos[i] - worldPos);
        vec3 vi1 = normalize(light.pos[(i + 1) % 4] - worldPos);
        vec3 ni = -normalize(cross(vi, vi1));
        vec3 ti = normalize(cross(vi, ni));
        float c;
        float delta;
        {
            float a = max(dot(vi, r), 1e-9);
            float b = max(dot(ti, r), 1e-9);
            c = sqrt(a * a + b * b);
            delta = atan(b / a);
        }
        float Imin = 0.0;
        float Imax = (pow(c, specFactor + 2.0) - 1.0) / (pow2(c) - 1.0);
        float xw = PI / 3.0 * sqrt(1.0 - pow2(c - c / float(specFactor)));
        float cosxw = cos(xw);
        float fxw = c * cosxw;
        float Ixw = (pow(fxw, specFactor + 2.0) - fxw) / (pow2(fxw) - 1.0);
        float yw = (Ixw - Imin) / (Imax - Imin);
        float a = (1.0 - yw - 4.0 * pow2(xw / PI)) / yw / pow2(xw);
        float Pmax = 1.0 / (1.0 + a * pow2(0.0));
        float Pmin = 1.0 / (1.0 + a * pow2(PI / 2.0));
        float s = (Imax - Imin) / (Pmax - Pmin);
        float t = Imin - s * Pmin;
        float Phi = acos(dot(vi, vi1));
        float sqrt_a = sqrt(a);
        float F = s / sqrt_a * (
            atan(sqrt_a * (Phi - delta)) - atan(-sqrt_a * delta)
        ) + t * Phi;
        float l = F * dot(ni, r);
        sp += max(l, 0.0);
	}
    return light.color * sp;
}
void main()
{
    vec3 cameraPos = vec3(0, 3, -5);
 
    float AxisY = 0.5;
    float AxisZ = 0.0;
	vec2 lightsPos = vec2(1.0);
    Quad light;
    light.pos = vec3[4](
        vec3(-1.75, 0.0 + lightsPos.x, lightsPos.y),
        vec3(-1.75, 0.5 + lightsPos.x, lightsPos.y),
        vec3( 1.75, 0.5 + lightsPos.x, lightsPos.y),
        vec3( 1.75, 0.0 + lightsPos.x, lightsPos.y)
    );
    float flagLerp = sin(iTime) * 0.5 + 0.5;
    light.color = mix(vec3(1, 0, 0), vec3(1, 1, 0), flagLerp);
    light.normal = vec3(0, 0, -1);
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = (gl_FragCoord - iResolution.xy / 2.0) / iResolution.x;
    vec3 front = normalize(vec3(0, -1, 2));
    vec3 right = normalize(cross(front, vec3(0, 1, 0)));
    vec3 up = cross(right, front);
    vec3 viewVec = normalize(front + right * uv.x + up * uv.y);

    // (cameraPos + viewVec * t).y = 0
    float t = -cameraPos.y / viewVec.y;
    vec3 worldPos = cameraPos + viewVec * t;
    vec3 color = texture(iChannel0, worldPos.xz).rgb;
    vec3 floorNormal = normalize(vec3(0, 1, 0) + (texture(iChannel0, worldPos.xz).rgb * 2.0 - 1.0) * 0.2);
    float specFactor = 32.0 * 2.0 + 1.0;
    float d = ray_triangle_intersection(light, cameraPos, viewVec);
    bool lightIntersect = false;
    if (d < t) {
        color = light.color;
        t = d;
        lightIntersect = true;
    }

    if (!lightIntersect) {
        color = getLightSpecular(light, worldPos, viewVec, floorNormal, specFactor) / 2.0 / PI;
 
    }
    
    gl_FragColor = vec4(color, 1.0);



}

""")

program = glCreateProgram()
glAttachShader(program, vertex)
glAttachShader(program, fragment)
glLinkProgram(program)
glUseProgram(program)

# Определяем массив цветов (по одному цвету для каждой вершины)

glutTimerFunc(10, calc, 0)
iResolution = glGetUniformLocation(program, "iResolution")
glUniform2f(iResolution, 512.0, 512.0)
tex = glGetUniformLocation(program, "iChannel0")
tt = read_texture()
#glUniform1i(tex, tt)
glutMainLoop()









